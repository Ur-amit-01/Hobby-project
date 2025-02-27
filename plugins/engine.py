
import openai

async def ai(query):
    openai.api_key = "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"  # Replace with your OpenAI API key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Using GPT-3.5 Turbo
        messages=[{"role": "user", "content": query}],
        max_tokens=200,  # Balanced response length
        n=1,
        temperature=0.9,
        timeout=5
    )
    return response["choices"][0]["message"]["content"].strip()

async def ask_ai(client, m, message):
    try:
        question = message.text.split(" ", 1)[1]  # Extract the query after the command
        response = await ai(question)  # Get AI response
        await m.edit(f"{response}")  # Send response back to user
    except Exception as e:
        await m.edit(f"❌ An error occurred: {e}")  # Handle errors
