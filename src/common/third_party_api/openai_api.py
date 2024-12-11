import openai

from server.src.common.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

class OpenAIAPI:
    @staticmethod
    def generate_embedding(text):
        response = openai.embeddings.create( # type: ignore
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    



class OpenAIAssistant():
    """
    This class is used to create an assistant and a vector store and a thread and a message and a run
    """
    vector_store_name: str
    assistant_name: str
    instructions: str
    assistant_id: str
    vector_store_id: str
    thread_id: str
    
    def __init__(self, vector_store_name: str, assistant_name: str, instructions: str):
        self.vector_store_name = vector_store_name
        self.assistant_name = assistant_name
        self.instructions = instructions
        # vector_store = self.is_vector_store_exists()
        # if not vector_store:
        #     self.create_vector_store(self.vector_store_name)
        # else:
        #     self.vector_store_id = vector_store.id
        # assistant = self.is_assistant_exists()
        # if not assistant:
        #     self.create_assistant(self.instructions)
        # else:
        #     self.assistant_id = assistant.id
        # self.create_thread()
    
    def init_assistant(self):
        self.create_vector_store(self.vector_store_name)
        self.create_assistant(self.instructions)
        # self.create_thread()
        
    def chat(self,content: str):
        return openai.chat.completions.create(model="gpt-4" ,messages=[{"role": "system", "content": f"You are a expert in the field of trading, financial analysis, and investment strategies, also your are expert in the field of python programming and data analysis especially using python polars library. Every time you are asked to create a calculation follow the instructions: {self.instructions}"},{"role": "user", "content": content}])

    def is_vector_store_exists(self):
        vector_stores = openai.beta.vector_stores.list()
        for vector_store in vector_stores:
            if vector_store.name == self.vector_store_name:
                return vector_store
        return False
    
    def create_vector_store(self, name: str):
        self.vector_store_id = openai.beta.vector_stores.create(name=name).id
    
    def update_vector_store(self, name: str):
        return openai.beta.vector_stores.update(vector_store_id=self.vector_store_id, name=name)
    
    def create_vector_store_files(self, file_id: str):
        return openai.beta.vector_stores.files.create(vector_store_id=self.vector_store_id, file_id=file_id)
    
    def is_assistant_exists(self):
        assistants = openai.beta.assistants.list()
        for assistant in assistants:
            if assistant.name == self.assistant_name:
                return assistant
        return False

    def create_assistant(self, instructions: str):
        self.assistant_id = openai.beta.assistants.create(
            model="gpt-4",
            instructions=instructions,
            name=self.assistant_name,
            response_format={'type': 'json_object'}
        ).id
    
    def retrieve_assistant(self):
        return openai.beta.assistants.retrieve(self.assistant_id)
                                          
    def create_thread(self):
        self.thread_id = openai.beta.threads.create(tool_resources={'file_search': {'vector_store_ids': [self.vector_store_id]}}).id

    def retrieve_thread(self):
        return openai.beta.threads.retrieve(self.thread_id)
    
    def create_message(self, content: str):
        return openai.beta.threads.messages.create(thread_id=self.thread_id, role="user", content=content)
    
    def create_run(self):
        return openai.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            tool_choice={'type': 'file_search'}
        )
    

