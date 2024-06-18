from setuptools import setup, find_packages

setup(
    name='ml_api_app',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Flask==3.0.3',
        'openai',
        'transformers',
        'chromadb',
        'python-dotenv',
        'streamlit',
    ],
)
