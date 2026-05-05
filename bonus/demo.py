# bonus/demo.py
"""Demo script for the HybridMemoryAgent.

The script populates a few episodic memories and then runs the five example
queries described in the bonus specification. The output prints the assembled
context for each query.
"""

from agent import HybridMemoryAgent


def main() -> None:
    agent = HybridMemoryAgent()

    # Populate a few example episodic memories (Vietnamese & English mix)
    example_memories = [
        "Đọc tài liệu về Kubernetes và kiến trúc microservice.",
        "Thảo luận về an ninh đám mây và compliance Việt Nam.",
        "Tìm hiểu về scaling infrastructure trong môi trường cloud.",
        "Tôi vừa đọc một bài báo về AI governance và đạo đức.",
        "Học cách tối ưu hóa tốc độ đọc cho tài liệu kỹ thuật.",
    ]
    for mem in example_memories:
        agent.remember(mem)
    # Add a memory that contains the default profile topics (cloud, ai, law)
    agent.remember("Bài viết về AI và cloud security rất hữu ích cho người dùng.")

    # The five demo queries required by the bonus spec
    queries = [
        "What have I read about Kubernetes?",            # Vector‑only lookup
        "Recommend what to read next",                   # Needs user profile
        "What am I focused on lately?",                 # Fresh activity
        "Documents about scaling infrastructure?",      # Paraphrase test
        "Give me a cloud security summary",            # Hybrid + profile
    ]

    for i, q in enumerate(queries, 1):
        print(f"\n--- Query {i}: {q} ---")
        print(agent.recall(q))


if __name__ == "__main__":
    main()
