"""
CodeBook parser module for parsing codebook files
"""

import os
from io import StringIO
from typing import Dict, Any, Optional, Tuple, List, Union, TextIO
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from datetime import datetime
import msgspec
from .models import (
    CodebookDocument,
    ConfigDocument,
    TaskDocument,
)


class CodebookParser:
    """Parser for codebook files"""

    def __init__(self, file_path: Optional[str] = None):
        """Initialize the parser with a file path"""
        self.file_path = file_path
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=2, offset=0)

    def parse_yaml(self, source: Union[str, StringIO, TextIO]) -> CodebookDocument:
        """解析 YAML 内容，保留注释和格式

        Args:
            source: YAML 内容源，可以是字符串或文件对象

        Returns:
            CodebookDocument: 解析后的代码本文档

        Raises:
            ValueError: 如果没有找到文档
            YAMLError: 如果 YAML 解析失败
        """
        documents = list(self.yaml.load_all(source))
        if not documents:
            raise ValueError("No documents found in YAML content")

        # 创建配置文档
        config_doc = ConfigDocument(documents[0], self.yaml)

        # 创建任务文档列表
        task_docs = []
        for task_data in documents[1:]:
            task_docs.append(TaskDocument(task_data, self.yaml))

        # 创建代码本文档
        return CodebookDocument(config_doc, task_docs, self.yaml)

    def parse_file(self, file_path: Optional[str] = None) -> CodebookDocument:
        """从文件路径解析代码本

        Args:
            file_path: 要解析的文件路径，如果未提供则使用初始化时的路径

        Returns:
            CodebookDocument: 解析后的代码本文档

        Raises:
            ValueError: 如果文件路径未设置或文件不存在
            YAMLError: 如果 YAML 解析失败
        """
        path = file_path or self.file_path
        if not path:
            raise ValueError("No file path provided")

        if not os.path.exists(path):
            raise ValueError(f"Codebook file does not exist: {path}")

        with open(path, "r", encoding="utf-8") as f:
            return self.parse_yaml(f)

    def dump_yaml(
        self, doc: Optional[CodebookDocument] = None, stream: Optional[TextIO] = None
    ) -> Optional[str]:
        """将代码本文档转回 YAML 格式，保留注释和格式

        Args:
            doc: 要保存的代码本文档，如果未提供则创建一个空文档
            stream: 如果提供，则直接写入该流

        Returns:
            Optional[str]: 如果未提供流，则返回 YAML 字符串
        """
        if doc is None:
            # 创建空的配置文档和任务文档列表
            config_doc = ConfigDocument(CommentedMap(), self.yaml)
            task_docs = []
            doc = CodebookDocument(config_doc, task_docs, self.yaml)

        return doc.dump(stream)

    def save_to_file(
        self, doc: Optional[CodebookDocument] = None, file_path: Optional[str] = None
    ) -> None:
        """将代码本文档保存到文件

        Args:
            doc: 要保存的代码本文档，如果未提供则使用内部文档
            file_path: 要保存的文件路径，如果未提供则使用初始化时的路径

        Raises:
            ValueError: 如果文件路径未设置
        """
        path = file_path or self.file_path
        if not path:
            raise ValueError("No file path provided")

        with open(path, "w", encoding="utf-8") as f:
            self.dump_yaml(doc, stream=f)
