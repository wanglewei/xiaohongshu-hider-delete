"""
小红书笔记批量管理工具安装配置
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements文件
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# 读取版本信息
def get_version():
    version_file = os.path.join("main.py")
    if os.path.exists(version_file):
        with open(version_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"

setup(
    name="xiaohongshu-note-manager",
    version=get_version(),
    author="Xiaohongshu Note Manager Team",
    author_email="",
    description="一个小红书笔记批量管理工具",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/xiaohongshu-note-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Natural Language :: Chinese (Simplified)",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "xiaohongshu-manager=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.rst"],
    },
    keywords=[
        "xiaohongshu",
        "note",
        "management",
        "selenium",
        "automation",
        "batch",
        "hide",
        "show",
        "delete",
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-username/xiaohongshu-note-manager/issues",
        "Source": "https://github.com/your-username/xiaohongshu-note-manager",
        "Documentation": "https://github.com/your-username/xiaohongshu-note-manager/blob/main/README.md",
    },
)
