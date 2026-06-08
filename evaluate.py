"""
Evaluation script: runs 5 test questions and prints a structured report.
"""
from vectorstore import get_collection
from rag import answer

TEST_QUESTIONS = [
    {
        "question": "Is Yuni Xia a good professor for discrete math?",
        "expected": "Yes — students say she curves heavily, is helpful, and the course is manageable if you attend lectures.",
    },
    {
        "question": "What do students say about Mohammad Hasan's CS class?",
        "expected": "Negative — students say he is unprepared, exams are very hard, and he lacks clarity.",
    },
    {
        "question": "What are students' biggest concerns about paying for college at IUI?",
        "expected": "Housing and living costs in Indianapolis, balancing work hours with study, and reliance on loans/FAFSA.",
    },
    {
        "question": "What electives do IUI CS students recommend?",
        "expected": "Students mention electives that are interesting or useful; the documents should contain specific course suggestions.",
    },
    {
        "question": "How is campus life at IUI compared to a traditional college experience?",
        "expected": "IUI is described as a commuter-heavy, urban campus with a strong community feel but limited traditional campus life.",
    },
]

ACCURACY_LABELS = ["Accurate", "Partially accurate", "Inaccurate"]
RETRIEVAL_LABELS = ["Relevant", "Partially relevant", "Off-target"]


def run_evaluation():
    col = get_collection()
    print("=" * 80)
    print("EVALUATION REPORT — IUI Unofficial Guide RAG System")
    print("=" * 80)

    for i, item in enumerate(TEST_QUESTIONS, 1):
        result = answer(item["question"], collection=col)
        chunks_used = [c["filename"] for c in result["chunks"]]

        print(f"\nQ{i}: {item['question']}")
        print(f"Expected: {item['expected']}")
        print(f"System response (first 400 chars): {result['answer'][:400]}")
        print(f"Chunks retrieved from: {', '.join(set(chunks_used))}")
        print("-" * 60)

    print("\nDone. Fill retrieval quality and response accuracy in README.md evaluation table.")


if __name__ == "__main__":
    run_evaluation()
