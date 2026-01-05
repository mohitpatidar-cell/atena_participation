# import google.generativeai as genai
# import os

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# client = genai.GenerativeModel(
#     model_name="gemini-2.5-flash",  # ✅ Fastest + accurate
#     generation_config={
#         "temperature": 0.0,
#         "top_p": 0.95,
#         "top_k": 40,
#         "max_output_tokens": 2048
#     }
# )
