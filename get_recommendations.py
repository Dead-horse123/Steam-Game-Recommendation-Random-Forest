import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


from nbconvert import PythonExporter
from nbconvert.preprocessors import ExecutePreprocessor
import nbformat
import os

dir_path = os.path.dirname(os.path.abspath(__file__))

def run_notebook(notebook_path):
    # Initialize exporter and preprocessor
    exporter = PythonExporter()
    preprocessor = ExecutePreprocessor(timeout=-1, kernel_name='python3')

    # Read the notebook file
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook_content = nbformat.read(f, as_version=4)

    # Export to Python code
    (python_code, resources) = exporter.from_notebook_node(notebook_content)

    # Execute the notebook
    executed_notebook, _ = preprocessor.preprocess(notebook_content, {'metadata': {'path': './'}})

    # Print execution summary
    print("Notebook execution completed.")

if __name__ == "__main__":
    notebook_path = dir_path + r"\random_forest_model.ipynb"  # Replace with your notebook path
    run_notebook(notebook_path)
