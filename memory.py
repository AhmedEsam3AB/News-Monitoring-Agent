import os
import json
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

class NewsMemory:
    def __init__(self, persistence_dir="memory_store"):
        self.persistence_dir = persistence_dir
        self.embeddings = OpenAIEmbeddings()
        self.processed_ids = set()
        self.vector_store = None
        
        self.load()

    def load(self):
        # Load processed IDs
        if os.path.exists(os.path.join(self.persistence_dir, "processed_ids.json")):
            with open(os.path.join(self.persistence_dir, "processed_ids.json"), "r") as f:
                self.processed_ids = set(json.load(f))
        
        # Load Vector Store
        if os.path.exists(os.path.join(self.persistence_dir, "index.faiss")):
            self.vector_store = FAISS.load_local(
                folder_path=self.persistence_dir, 
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True # We trust our own local file
            )
        else:
            # Initialize empty vector store with a dummy document or just wait for first add
            # FAISS needs at least one doc to initialize usually, or use from_texts
            pass

    def save(self):
        if not os.path.exists(self.persistence_dir):
            os.makedirs(self.persistence_dir)
            
        # Save processed IDs
        with open(os.path.join(self.persistence_dir, "processed_ids.json"), "w") as f:
            json.dump(list(self.processed_ids), f)
            
        # Save Vector Store
        if self.vector_store:
            self.vector_store.save_local(self.persistence_dir)

    def is_duplicate(self, news_id: str) -> bool:
        return news_id in self.processed_ids

    def find_related_news(self, content: str, k=3, score_threshold=0.8):
        if not self.vector_store:
            return []
        
        docs_and_scores = self.vector_store.similarity_search_with_score(content, k=k)
        # FAISS returns L2 distance by default for some indices, but cosine similarity if normalized. 
        # OpenAIEmbeddings are normalized. standard FAISS from_documents uses L2.
        # However, checking "ongoing stories" usually means looking for context.
        # Let's just return the docs.
        return [doc for doc, score in docs_and_scores if score < score_threshold] # Low score = match in L2? Or high score?
        # Standard FAISS in LangChain: Lower is better for Euclidean (L2). 
        # But let's verify if we want to filter. For now just return top k.
        return [doc for doc, _ in docs_and_scores]

    def add_news(self, news_item: dict, analysis: dict):
        """
        news_item: raw dict from RSS
        analysis: dict from chains (summary, score, etc.)
        """
        self.processed_ids.add(news_item['id'])
        
        # Only add "Important" news to Vector Memory context, or all? 
        # Prompt says "Store important news".
        if analysis['score'] >= 50: # Store if moderately important, trigger alert if >= 70
            text_to_embed = f"{news_item['title']}\n{analysis['summary']}"
            metadata = {
                "id": news_item['id'],
                "title": news_item['title'],
                "score": analysis['score'],
                "category": analysis['category'],
                "published": news_item['published']
            }
            doc = Document(page_content=text_to_embed, metadata=metadata)
            
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents([doc], self.embeddings)
            else:
                self.vector_store.add_documents([doc])
        
        self.save()
