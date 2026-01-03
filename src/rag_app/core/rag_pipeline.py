"""
RAG Pipeline for query processing and response generation
"""
import ollama
from typing import List, Dict
from .. import config
from .embedding_manager import EmbeddingManager
from .milvus_manager import MilvusManager


class RAGPipeline:
    """RAG pipeline for retrieval-augmented generation"""
    
    def __init__(self, embedding_manager: EmbeddingManager, milvus_manager: MilvusManager,
                 ollama_model: str = None, ollama_base_url: str = None):
        """
        Initialize RAG pipeline
        
        Args:
            embedding_manager: EmbeddingManager instance
            milvus_manager: MilvusManager instance
            ollama_model: Ollama model name
            ollama_base_url: Ollama base URL
        """
        self.embedding_manager = embedding_manager
        self.milvus_manager = milvus_manager
        self.ollama_model = ollama_model or config.OLLAMA_MODEL
        self.ollama_base_url = ollama_base_url or config.OLLAMA_BASE_URL
        
        # Configure ollama client
        self.client = ollama.Client(host=self.ollama_base_url)
        print(f"RAG Pipeline initialized with model: {self.ollama_model}")
    
    def retrieve_context(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Retrieve relevant context for a query
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant documents
        """
        # Generate query embedding
        query_embedding = self.embedding_manager.generate_embedding(query)
        
        # Search in Milvus
        results = self.milvus_manager.search(query_embedding, top_k)
        
        return results
    
    def format_context(self, results: List[Dict]) -> str:
        """
        Format retrieved documents into context string
        
        Args:
            results: List of search results
            
        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant context found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Document {i}] (Source: {result['source']}, Score: {result['score']:.3f})\n"
                f"{result['text']}\n"
            )
        
        return "\n".join(context_parts)
    
    def generate_prompt(self, query: str, context: str) -> str:
        """
        Generate prompt for the LLM
        
        Args:
            query: User query
            context: Retrieved context
            
        Returns:
            Formatted prompt
        """
        prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's question. 
If the answer cannot be found in the context, say so clearly.

Context:
{context}

Question: {query}

Answer:"""
        return prompt
    
    def generate_response(self, prompt: str, stream: bool = False) -> str:
        """
        Generate response using Ollama
        
        Args:
            prompt: Formatted prompt
            stream: Whether to stream the response
            
        Returns:
            Generated response
        """
        try:
            if stream:
                response_text = ""
                stream_response = self.client.chat(
                    model=self.ollama_model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True
                )
                
                for chunk in stream_response:
                    if 'message' in chunk and 'content' in chunk['message']:
                        content = chunk['message']['content']
                        print(content, end='', flush=True)
                        response_text += content
                print()  # New line after streaming
                return response_text
            else:
                response = self.client.chat(
                    model=self.ollama_model,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response['message']['content']
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def query(self, query: str, top_k: int = None, stream: bool = False, 
              show_context: bool = False) -> Dict:
        """
        Process a query through the RAG pipeline
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            stream: Whether to stream the response
            show_context: Whether to include context in the result
            
        Returns:
            Dictionary with response and metadata
        """
        print(f"\nProcessing query: {query}")
        
        # Retrieve context
        print("Retrieving relevant documents...")
        results = self.retrieve_context(query, top_k)
        print(f"Retrieved {len(results)} documents")
        
        # Format context
        context = self.format_context(results)
        
        # Generate prompt
        prompt = self.generate_prompt(query, context)
        
        # Generate response
        print("Generating response...")
        response = self.generate_response(prompt, stream)
        
        result = {
            "query": query,
            "response": response,
            "num_sources": len(results),
            "sources": [r['source'] for r in results]
        }
        
        if show_context:
            result["context"] = context
            result["retrieved_documents"] = results
        
        return result
    
    def chat(self, stream: bool = True):
        """
        Interactive chat interface
        
        Args:
            stream: Whether to stream responses
        """
        print("\n" + "="*60)
        print("RAG Chat Interface")
        print("Type 'exit' or 'quit' to end the conversation")
        print("="*60 + "\n")
        
        while True:
            try:
                query = input("\nYou: ").strip()
                
                if query.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                
                if not query:
                    continue
                
                print("\nAssistant: ", end='')
                result = self.query(query, stream=stream)
                
                if not stream:
                    print(result['response'])
                
                print(f"\n[Sources: {', '.join(set(result['sources']))}]")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")

# Made with Bob
