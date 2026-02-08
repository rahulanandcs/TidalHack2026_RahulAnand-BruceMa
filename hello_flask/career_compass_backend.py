from google import genai

client = genai.Client(api_key = "AIzaSyCSIqtgnFftPSlrVSA8iWswlueyLZyY1cs")

#image = Image.open()
resume_file = open("C:/Users/41866/.vscode/CareerCompass/resume_information.txt", "r")
companies_file = open("C:/Users/41866/.vscode/CareerCompass/company_information.txt", "r")
response_format_file = open("C:/Users/41866/.vscode/CareerCompass/response_format.txt", "r")
resume = resume_file.read()
companies = companies_file.read()
format = response_format_file.read()
resume_file.close()
companies_file.close()
response_format_file.close()

question = format + "\n\n\nThis is my resume: \n" + resume + "\n\n\n" + "These are the company information: \n" + companies

response = client.models.generate_content(
    model = "gemini-3-flash-preview", contents = question
)
print(response.text)