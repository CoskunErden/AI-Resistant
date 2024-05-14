from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from services.schemas import GenericRequest, ChatResponse, Message, GCS_File
from dependencies import get_db
from utils.auth import key_check
from utils.request_handler import validate_multipart_form_data
from services.firestore import get_data
from services.tool_registry import validate_inputs
import json

from features.dynamo.core import executor as dynamo_executor
from features.quizzify.core import executor as quizzify_executor


router = APIRouter()

@router.get("/")
def read_root():
    return {"Hello": "World"}


async def get_files(request: Request):
    form = await request.form()
    files = form.getlist("files")
    valid_files = [file for file in files if file != '']
    return valid_files

@router.post("/submit-tool")
async def submit_tool(
    data: GenericRequest,
    db = Depends(get_db),
    #_ = Depends(key_check)
):  
    try:        
        # Unpack GenericRequest for tool data
        request_data = data.tool_data
    
        requested_tool = get_data(db, "tools", str(request_data.tool_id)) # Tools registry has IDs as strings
        if requested_tool is None:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        # Validate inputs from firestore and request
        inputs = requested_tool['inputs']    
        request_inputs_dict = {input.name: input.value for input in request_data.inputs}
        
        print(inputs)
        
        # Extract 'files' input by attribute access
        file_objects = next((input_item.value for input_item in request_data.inputs if input_item.name == "files"), None)
        # Mutate to GCS_File objects
        if file_objects and isinstance(file_objects, list):
            file_objects = [
                GCS_File(
                    filePath=file_object['filePath'], 
                    url=file_object['url'],
                    filename=file_object['filename']
                ) 
                for file_object in file_objects
            ]
        
        print(f"Request inputs: {request_inputs_dict}")
        if not validate_inputs(request_inputs_dict, inputs):
            raise HTTPException(status_code=400, detail="Input validation failed")
        print(f"Inputs validated")
    
        # Available Tools
        tool_functions = {
            "0": quizzify_executor,
            "1": dynamo_executor,
        }
        
        # Set Executor based on tool requested
        execute_function = tool_functions.get(str(request_data.tool_id))
        if not execute_function:
            raise HTTPException(status_code=404, detail="Tool executable not found")
        
        # If files, append to request_inputs_dict
        if file_objects:
            request_inputs_dict["files"] = file_objects
            print(f"Files appended to request inputs: {len(file_objects)}")
        
        # Call execute with request_inputs_dict
        #print(f"Executing tool {request_data.tool_id} with inputs: {request_inputs_dict}")
        try: 
            result = execute_function(**request_inputs_dict)
        except Exception as e:
            print(f"Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
        return {"message": "success", "files": len(file_objects), "data": result}
    
    
    except json.JSONDecodeError as e:
        print(f"JSON Decoding error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"JSON Decoding error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/gcs-upload")
async def gcs_upload(request: GenericRequest):
    # destructure the request
    # grab the file URL from request
    # use GCS to download file
    from services.gcp import download_from_gcs
    from features.quizzify.tools import GCSLoader, GCS_File
    
    inputs = request.tool_data.inputs
    file_objects = next((input.value for input in inputs if input.name == "files"), None)
    
    file_objects = [
        GCS_File(
            filePath=file_object['filePath'], 
            url=file_object['url'],
            filename=file_object['filename']
        ) 
        for file_object in file_objects
    ]
    
    if file_objects:
        loader = GCSLoader()
        file_documents = loader.load(file_objects)
    
    return {"data": (file_documents[0])}


@router.post("/chat")
async def chat(request: GenericRequest, _ = Depends(key_check)):
    from features.Kaichat.core import executor as kaichat_executor
    
    user_name = request.user.fullName
    chat_messages = request.messages
    user_query = chat_messages[-1].payload.text
    
    response = kaichat_executor(user_name=user_name, user_query=user_query, messages=chat_messages)
    
    formatted_response = Message(
        role="ai",
        type="text",
        payload={"text": response}
    )
    
    return {"data": [formatted_response]}

