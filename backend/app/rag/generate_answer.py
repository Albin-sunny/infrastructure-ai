from langchain_groq import ChatGroq
from dotenv import load_dotenv
from backend.app.rag.retriever import retrieve
import os

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_answer(question,history_text=""):

    try:

        followup_words = [
            "that",
            "this",
            "it",
            "them",
            "those",
            "these",
            "how",
            "why",
            "explain",
            "what about that"
        ]

        search_query = question

        if any(word in question.lower() for word in followup_words):
            search_query = f"""
        Previous Conversation:
        {history_text}

        Current Question:
        {question}

        Search using the previous engineering topic and answer the current question.
        """

        print("\nSEARCH QUERY")
        print(search_query)
        print()

        retrieved_chunks = retrieve(
            search_query,
            k=8
        )

        if not retrieved_chunks:
            return (
                "No relevant information was found "
                "in the engineering manuals."
            )

        context = "\n\n".join(
            retrieved_chunks
        )

        print("\n====================")
        print("RETRIEVED CHUNKS")
        print("====================")
        print(context)
        print("====================\n")

        prompt = f"""
You are an Infrastructure Inspection and Bridge Engineering Assistant.

Your job is to answer ONLY from the provided engineering manuals (Context) and the Conversation History.

========================
RULES
========================
- Never repeat previous questions or previous answers its mnaditory.
- Never mention "Conversation History", "Context", or "retrieved chunks" in your response.
- Never explain how you generated the answer.
- Return only the final engineering answer.
- Include all relevant steps found across the retrieved context.
1. NEVER use outside knowledge.

2. NEVER invent information.

3. If the answer is not present in the context, reply:
"The provided engineering manuals do not contain this information."

4. Ignore unrelated retrieved chunks.

5. Combine information from multiple retrieved chunks when they describe the same engineering topic.

6. Quote product names exactly as written.

7. Never mix information from different repair methods.

8. If multiple retrieved chunks describe different parts of the same repair procedure, merge them into one complete answer.

9. Never stop after the first matching chunk.

10. Use every relevant chunk before producing the final answer.

========================
FOLLOW-UP QUESTIONS
========================

If the current question contains words such as:

that
this
it
them
those
these
how
how do that
what next
why
explain
continue

then:

- First determine the MAIN engineering topic from the Conversation History.
- Ignore unrelated retrieved chunks.
- Assume the user is continuing the previous engineering discussion unless the user clearly changes the topic.
- Answer about the previously discussed engineering topic.

Example:

User:
Deep crack repair method

User:
How do that

Meaning:

How do I perform the deep crack repair method?

NOT:

How do I perform a random repair found inside another chunk?

========================
REPAIR QUESTIONS
========================

If the user asks about:

repair
method
procedure
installation
inspection
maintenance
replacement
construction

Then:

- Explain the repair method clearly.
- List every repair step found in the context.
- Keep the steps in their original order whenever possible.
- Mention required materials if present.
- Mention precautions if present.
- Mention alternative methods if present.
- Do not create additional steps.

========================
OUTPUT FORMAT
========================

If repair steps exist:

Repair Method:
<method>

Steps:
1.
2.
3.
...

Materials:
...

Precautions:
...

Notes:
...

If no steps exist, answer naturally using only the context.

========================
Conversation History
========================

{history_text}

========================
Engineering Context
========================

{context}

========================
Current Question
========================

{question}

========================
Answer
========================
"""

        response = llm.invoke(prompt)

        return response.content

    except Exception as e:

        raise Exception(
            f"Error generating answer: {str(e)}"
        )