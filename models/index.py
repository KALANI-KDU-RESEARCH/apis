import textwrap
import google.generativeai as genai
from IPython.display import Markdown

#THIS IS BASED ON GOOGLE LLM's
def predict(query):
    def to_markdown(text):
        text = text.replace('•', '  *')
        return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

    genai.configure(api_key='AIzaSyD4z63UDBeKGjktRqd_N_SOEmFifQhJCm4')

    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)

    model = genai.GenerativeModel('gemini-pro')

    response = model.generate_content(query)

    print(response.text)

    return to_markdown(response.text)

#SAMPLE => give me micro entrepreneur business ideas for farming do not act like a assistant point form with urls and some images