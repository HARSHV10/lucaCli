from setuptools import setup, find_packages

setup(
    name='luca',
    version='0.1.0',
    py_modules=['luca', 'config_manager', 'llm_engine', 'command_executor'],
    install_requires=[
        'click',
        'openai',
        'requests',
        'colorama',
    ],
    entry_points={
        'console_scripts': [
            'luca = luca:cli',
        ],
    },
)
