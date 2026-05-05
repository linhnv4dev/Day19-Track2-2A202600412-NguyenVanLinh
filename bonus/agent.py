# bonus/agent.py
"""Simple POC implementation of the HybridMemoryAgent.

The real system would integrate with a vector DB (e.g., Qdrant), a feature store (Feast)
and a streaming layer. For the purpose of the bonus challenge we provide a lightweight
in‑memory mock that satisfies the required API:

- ``remember(text, user_id)`` stores the raw text as an episodic memory chunk.
- ``recall(query, user_id)`` performs a naïve keyword search over stored memories,
  fetches the user profile from an in‑memory feature dict and returns a formatted
  context string.

This implementation is deliberately simple – it focuses on the architectural
decisions rather than performance.
"""

from __future__ import annotations
from collections import defaultdict
from typing import List, Dict

import os
import openai
import unicodedata, re
from typing import List

# Set OpenAI API key from environment (optional fallback)
openai.api_key = os.getenv("OPENAI_API_KEY")

# In‑memory stores (mocking vector DB and feature store)
_EPISODIC_STORE: Dict[str, List[str]] = defaultdict(list)  # user_id -> list of memories
_FEATURE_STORE: Dict[str, Dict[str, str]] = defaultdict(dict)  # user_id -> feature dict


class HybridMemoryAgent:
    """Hybrid memory agent combining episodic, profile, and recent activity.

    The methods are intentionally minimal; they demonstrate how the three
    sources would be combined into a final context.
    """

    def __init__(self) -> None:
        # Initialise a default profile for demonstration purposes.
        # In a real system this would be loaded from Feast.
        self._ensure_default_profile("u_001")

    # ---------------------------------------------------------------------
    # Helper methods
    # ---------------------------------------------------------------------
    # Helper: normalize text (lowercase, strip diacritics, split words)
    def _normalize(self, txt: str) -> List[str]:
        txt = txt.lower()
        txt = unicodedata.normalize('NFKD', txt)
        txt = txt.encode('ascii', 'ignore').decode('ascii')
        return re.findall(r'\w+', txt)

    # Helper: generate fallback response via OpenAI when no memory exists
    def _generate_fallback(self, query: str) -> str:
        prompt = f"User asks: '{query}'. Generate a short informative answer as if the system had relevant memory."
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant providing concise context snippets."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=80,
                temperature=0.7,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"(fallback generation failed: {e})"


    def _ensure_default_profile(self, user_id: str) -> None:
        """Populate a minimal profile if none exists for *user_id*."""
        if user_id not in _FEATURE_STORE:
            _FEATURE_STORE[user_id] = {
                "preferred_language": "vi",
                "topic_affinity": "cloud,ai,law",
                "reading_speed_wpm": "200",
                "active_hours": "9-22",
                "expertise_level": "intermediate",
            }

    def _semantic_search(self, query: str, memories: List[str], top_k: int = 3) -> List[str]:
        """Normalized keyword search with fallback to OpenAI generation when no memory exists."""
        q_terms = set(self._normalize(query))
        results: List[str] = []
        for mem in memories:
            mem_terms = set(self._normalize(mem))
            if q_terms & mem_terms:
                results.append(mem)
            if len(results) >= top_k:
                break
        # Fallback: if no match and we have any memory, use the most recent one
        if not results and memories:
            results.append(memories[-1])
        # Final fallback: generate a synthetic response via OpenAI if still empty
        if not results:
            generated = self._generate_fallback(query)
            results.append(generated)
        return results
        """Very naive keyword‑based retrieval.

        A real implementation would embed *query* and *memories* and perform a
        nearest‑neighbors lookup. Here we simply return the first *top_k*
        memories that contain any word from the query.
        """
        q_terms = set(query.lower().split())
        results: List[str] = []
        for mem in memories:
            if q_terms & set(mem.lower().split()):
                results.append(mem)
            if len(results) >= top_k:
                break
        return results

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def _semantic_chunk(self, text: str, max_tokens: int = 200) -> List[str]:
        """Mock semantic chunking.
        Splits *text* into roughly *max_tokens* word chunks with a 20% overlap.
        This mimics the design decision in ARCHITECTURE.md without needing real tokenizers.
        """
        words = text.split()
        if not words:
            return []
        chunk_size = max_tokens
        overlap = int(chunk_size * 0.2)
        chunks: List[str] = []
        i = 0
        while i < len(words):
            end = i + chunk_size
            chunk = " ".join(words[i:end])
            chunks.append(chunk)
            i = end - overlap  # step back for overlap
        return chunks

    def remember(self, text: str, user_id: str = "u_001") -> None:
        """Add a new piece of episodic memory for *user_id*.

        The text is split into semantic chunks (mock) and each chunk is stored.
        In a real system each chunk would be embedded and inserted into a vector DB.
        """
        chunks = self._semantic_chunk(text)
        for c in chunks:
            _EPISODIC_STORE[user_id].append(c)
        # Ensure a profile exists so ``recall`` can always return something.
        self._ensure_default_profile(user_id)

    def recall(self, query: str, user_id: str = "u_001") -> str:
        """Retrieve top‑K memories, enrich with profile features, and assemble context.

        Steps:
        1. Semantic keyword search over episodic memories.
        2. If profile *topic_affinity* contains terms that appear in the query, give
           priority to memories that also mention those topics (simple enrichment).
        3. Assemble a multi‑line context string containing retrieved memories,
           the user profile and a recent‑activity placeholder.
        """
        memories = _EPISODIC_STORE.get(user_id, [])
        # 1️⃣ Base retrieval
        base_memories = self._semantic_search(query, memories)

        # 2️⃣ Profile‑driven enrichment (only for demonstration)
        profile = _FEATURE_STORE.get(user_id, {})
        topics = set(profile.get("topic_affinity", "").replace(",", " ").split())
        query_terms = set(self._normalize(query))
        # If query overlaps with profile topics, boost memories containing those topics
        if topics & query_terms:
            enriched: List[str] = []
            for mem in memories:
                mem_terms = set(self._normalize(mem))
                if topics & mem_terms:
                    enriched.append(mem)
                if len(enriched) >= 3:
                    break
            # If we got enriched results, replace base_memories
            if enriched:
                top_memories = enriched
            else:
                top_memories = base_memories
        else:
            top_memories = base_memories

        # 3️⃣ Mock recent activity – the latest stored chunk
        recent_activity = memories[-1] if memories else "(no recent activity)"

        parts = ["--- Retrieved Memories ---"]
        if top_memories:
            parts.extend([f"- {m}" for m in top_memories])
        else:
            parts.append("(no relevant memories found)")

        parts.append("--- User Profile ---")
        for k, v in profile.items():
            parts.append(f"{k}: {v}")

        parts.append("--- Recent Activity ---")
        parts.append(recent_activity)

        return "\n".join(parts)

# When run as a script, demonstrate a tiny workflow.
if __name__ == "__main__":
    agent = HybridMemoryAgent()
    agent.remember("Đọc tài liệu về Kubernetes và kiến trúc microservice.")
    agent.remember("Thảo luận về an ninh đám mây và compliance Việt Nam.")
    print(agent.recall("Kubernetes"))
