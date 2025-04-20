from typing import List, Optional, Dict, Any, Literal, Union, TextIO
from datetime import datetime
import msgspec
from io import StringIO
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq


class Metadata(msgspec.Struct, kw_only=True):
    """Codebook metadata"""

    name: str
    version: str
    description: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ModelConfig(msgspec.Struct, kw_only=True):
    """Model configuration"""

    model: str = "gpt-4"
    chat_model: str = "gpt-4"
    code_model: str = "gpt-4"
    index_filter_model: str = ""
    generate_rerank_model: str = ""
    emb_model: str = ""
    commit_model: str = ""
    vl_model: str = ""
    designer_model: str = ""
    voice2text_model: str = ""
    sd_model: str = ""


class Settings(msgspec.Struct, kw_only=True):
    """Global settings"""

    # Context filtering and indexing
    skip_filter_index: bool = False
    skip_build_index: bool = False
    include_project_structure: bool = True

    # Context processing
    conversation_prune_safe_zone_tokens: int = 51200
    index_filter_model_max_input_length: int = 51200

    # Code generation and merging
    auto_merge: Literal["editblock", "wholefile", "diff", "strict_diff"] = "editblock"
    enable_auto_fix_lint: bool = False
    enable_auto_fix_merge: bool = False
    generate_times_same_model: int = 1

    # Advanced features
    enable_task_history: bool = False
    enable_active_context: bool = False
    enable_agentic_filter: bool = False
    enable_agentic_edit: bool = False

    # Result tracking
    track_tokens: bool = True
    track_cost: bool = True
    track_tools: bool = True
    track_mcp: bool = True


class Context(msgspec.Struct, kw_only=True):
    """Context configuration"""

    files: List[str] = msgspec.field(default_factory=list)
    lib: List[str] = msgspec.field(default_factory=list)
    docs: List[str] = msgspec.field(default_factory=list)


class Environment(msgspec.Struct, kw_only=True):
    """Runtime environment"""

    in_cursor: bool = True
    in_jetbrains: bool = False
    in_code: bool = False
    in_windsurf: bool = False


class Status(msgspec.Struct, kw_only=True):
    """Runtime status"""

    # Execution control
    run: bool = False
    parallel: bool = False
    max_parallel: int = 1

    # Progress tracking
    current_task: Optional[str] = None
    completed_tasks: List[str] = msgspec.field(default_factory=list)
    failed_tasks: List[str] = msgspec.field(default_factory=list)

    # Resource monitoring
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None

    # Error handling
    stop_on_error: bool = True
    retry_count: int = 0
    error_threshold: int = 3


class Task(msgspec.Struct, kw_only=True):
    """Task definition"""

    task: str
    cmd: str
    priority: int
    scratch: bool = False
    content: str = ""
    models: Dict[str, Any] = msgspec.field(default_factory=dict)
    refs: List[str] = msgspec.field(default_factory=list)


class CodebookConfig(msgspec.Struct, kw_only=True):
    """代码本配置，包含首文档的所有内容"""

    metadata: Metadata
    models: ModelConfig
    settings: Settings
    context: Context
    env: Environment
    status: Status


class CommentedDocument:
    """带注释的文档基类"""

    def __init__(self, data: CommentedMap, yaml: Optional[YAML] = None):
        self._data = data
        self._yaml = yaml or YAML()
        self._yaml.preserve_quotes = True
        self._yaml.indent(mapping=2, sequence=2, offset=0)

    def comment_out(self, key: str) -> None:
        """将键注释掉"""
        if key in self._data:
            value = self._data[key]
            self._data.yaml_add_eol_comment(f"# {value}", key)
            del self._data[key]

    def comment_in(self, key: str) -> None:
        """取消键的注释"""
        if key in self._data.ca.items:
            comment = self._data.ca.items[key]
            if comment and comment[2]:  # before comment
                value = comment[2].value.strip("# ")
                self._data[key] = self._yaml.load(value)
                self._data.yaml_set_comment_before_after_key(
                    key, before=None, after=None
                )

    def dump(self, stream: Optional[TextIO] = None) -> Optional[str]:
        """将文档转回 YAML 格式

        Args:
            stream: 如果提供，则直接写入该流

        Returns:
            Optional[str]: 如果未提供流，则返回 YAML 字符串
        """
        if stream:
            self._yaml.dump(self._data, stream)
            return None
        else:
            output = StringIO()
            self._yaml.dump(self._data, output)
            return output.getvalue()


class ConfigDocument(CommentedDocument):
    """代码本配置文档"""

    def __init__(self, data: CommentedMap, yaml: Optional[YAML] = None):
        super().__init__(data, yaml)
        self.metadata = self._parse_metadata(data.get("metadata", {}))
        self.models = self._parse_models(data.get("models", {}))
        self.settings = self._parse_settings(data.get("settings", {}))
        self.context = self._parse_context(data.get("context", {}))
        self.env = self._parse_env(data.get("env", {}))
        self.status = self._parse_status(data.get("status", {}))

    def update(self, codebook: CodebookConfig) -> None:
        """更新文档值"""
        self._update_with_comments("metadata", self._dump_metadata(codebook.metadata))
        self._update_with_comments("models", self._dump_models(codebook.models))
        self._update_with_comments("settings", self._dump_settings(codebook.settings))
        self._update_with_comments("context", self._dump_context(codebook.context))
        self._update_with_comments("env", self._dump_env(codebook.env))
        self._update_with_comments("status", self._dump_status(codebook.status))

    def _update_with_comments(self, key: str, new_data: Dict[str, Any]) -> None:
        """更新值并保留注释"""
        if key in self._data:
            comments = self._data.ca.items.get(key)
            self._data[key] = new_data
            if comments:
                self._data.yaml_set_comment_before_after_key(
                    key, before=comments[2], after=comments[3]
                )

    def _parse_metadata(self, data: Dict[str, Any]) -> Metadata:
        """解析元数据部分"""
        return Metadata(**data)

    def _parse_models(self, data: Dict[str, Any]) -> ModelConfig:
        """解析模型配置"""
        return ModelConfig(**data)

    def _parse_settings(self, data: Dict[str, Any]) -> Settings:
        """解析设置"""
        return Settings(**data)

    def _parse_context(self, data: Dict[str, Any]) -> Context:
        """解析上下文"""
        return Context(**data)

    def _parse_env(self, data: Dict[str, Any]) -> Environment:
        """解析环境配置"""
        return Environment(**data)

    def _parse_status(self, data: Dict[str, Any]) -> Status:
        """解析状态"""
        return Status(**data)

    def _dump_metadata(self, metadata: Metadata) -> Dict[str, Any]:
        """转换元数据到字典"""
        return msgspec.to_builtins(metadata)

    def _dump_models(self, models: ModelConfig) -> Dict[str, Any]:
        """转换模型配置到字典"""
        return msgspec.to_builtins(models)

    def _dump_settings(self, settings: Settings) -> Dict[str, Any]:
        """转换设置到字典"""
        return msgspec.to_builtins(settings)

    def _dump_context(self, context: Context) -> Dict[str, Any]:
        """转换上下文到字典"""
        return msgspec.to_builtins(context)

    def _dump_env(self, env: Environment) -> Dict[str, Any]:
        """转换环境配置到字典"""
        return msgspec.to_builtins(env)

    def _dump_status(self, status: Status) -> Dict[str, Any]:
        """转换状态到字典"""
        return msgspec.to_builtins(status)


class TaskDocument(CommentedDocument):
    """任务文档"""

    def __init__(self, data: CommentedMap, yaml: Optional[YAML] = None):
        super().__init__(data, yaml)
        self.task = self._parse_task(data)

    def update(self, task: Task) -> None:
        """更新任务值"""
        task_data = self._dump_task(task)
        for k, v in task_data.items():
            if k in self._data:
                comments = self._data.ca.items.get(k)
                self._data[k] = v
                if comments:
                    self._data.yaml_set_comment_before_after_key(
                        k, before=comments[2], after=comments[3]
                    )
            else:
                self._data[k] = v

    def _parse_task(self, data: Dict[str, Any]) -> Task:
        """解析任务"""
        return Task(**data)

    def _dump_task(self, task: Task) -> Dict[str, Any]:
        """转换任务到字典"""
        return msgspec.to_builtins(task)


class CodebookDocument:
    """代码本文档，包含配置和任务文档"""

    def __init__(
        self,
        config: ConfigDocument,
        tasks: List[TaskDocument],
        yaml: Optional[YAML] = None,
    ):
        self.config = config
        self.tasks = tasks
        self._yaml = yaml or YAML()
        self._yaml.preserve_quotes = True
        self._yaml.indent(mapping=2, sequence=2, offset=0)

    def dump(self, stream: Optional[TextIO] = None) -> Optional[str]:
        """将文档转回 YAML 格式

        Args:
            stream: 如果提供，则直接写入该流

        Returns:
            Optional[str]: 如果未提供流，则返回 YAML 字符串
        """
        if stream:
            # 写入配置文档
            stream.write("---\n# Codebook configuration\n")
            self.config.dump(stream)

            # 写入任务文档
            for task_doc in self.tasks:
                stream.write("---\n# Task document\n")
                task_doc.dump(stream)
            return None
        else:
            output = []
            output.append("---\n# Codebook configuration\n")
            output.append(self.config.dump())
            for task_doc in self.tasks:
                output.append("---\n# Task document\n")
                output.append(task_doc.dump())
            return "".join(output)
