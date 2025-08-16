from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Any, Dict, TypeVar

# 类型注册表
ALLOWED_CONFIG_TYPES = []

# 定义 ConfigBase 基类
class ConfigBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid"  # 禁止额外字段
    )

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        # 自定义序列化，确保使用子类字段
        return super().model_dump(**kwargs)
T = TypeVar('T', bound=ConfigBase)
# Test2 模型
class Test2(ConfigBase):
    sql: str = Field(..., description="SQL 查询字符串")

# Test3 模型
class Test3(ConfigBase):
    script: str = Field(..., description="脚本内容")

# 注册允许的子类
ALLOWED_CONFIG_TYPES.extend([Test2, Test3])

# Test 模型
class Test(BaseModel):
    run_cmd: str = Field(..., description="运行的命令")

# Test1 模型
class Test1(BaseModel):
    test: Test
    config: T = Field(..., description="配置，支持 ConfigBase 的子类")

    model_config = ConfigDict(
        extra="forbid"  # 确保字段严格性
    )

# CreateTest 模型
class CreateTest(Test1):
    test2: Test2 = Field(..., description="包含 SQL 查询的 Test2 实例")
    run_cmd: str = Field("sh test.sh", description="测试运行的命令", exclude=True)

    def model_post_init(self, __context: Any) -> None:
        if self.test:
            self.test.run_cmd = self.run_cmd

    model_config = ConfigDict(
        extra="forbid"  # 仅保留必要配置
    )

# 测试代码
def test_create_test():
    test_instance = Test(run_cmd="default_cmd")
    test2_instance = Test2(sql="SELECT * FROM users")
    config_instance = Test3(script="echo hello")

    # 调试：检查 config_instance
    print("config_instance:", config_instance.model_dump_json(indent=2))

    # 创建 CreateTest 实例
    create_test = CreateTest(
        test=test_instance,
        config=config_instance,
        test2=test2_instance,
        run_cmd="sh custom_test.sh"
    )

    # 调试：检查 create_test.config
    print("create_test.config:", create_test.config.model_dump_json(indent=2))

    # 调试：检查 config 类型
    print("config type:", type(create_test.config))

    # 最终输出
    print("最终输出:", create_test.model_dump_json(indent=2))

if __name__ == "__main__":
    test_create_test()







您的问题非常合理，当需要支持大量子类时，使用 Union[Test2, Test3, ..., Test100] 显然不可行。以下是几种可扩展的解决方案，适用于 Pydantic 模型动态支持 ConfigBase 的任意子类：

方案 1：使用 TypeVar 泛型（Pydantic V2 推荐）

通过泛型绑定到 ConfigBase 的子类，保持类型安全且无需枚举所有子类：
from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T', bound=ConfigBase)  # 限定为 ConfigBase 的子类

class Test1(BaseModel, Generic[T]):
    test: Test
    config: T = Field(..., description="支持任意 ConfigBase 的子类")

# 使用时指定具体子类
create_test = Test1[Test3](  # 明确指定子类类型
    test=test_instance,
    config=config_instance  # 必须传入 Test3 实例
)


优点：类型安全，IDE 可自动补全。  
缺点：需在实例化时显式指定泛型类型。

方案 2：动态 Union 生成（适用于运行时注册的子类）

在运行时动态生成 Union 类型，适合插件式架构：
from typing import Union, get_args, set_type_params

# 注册所有子类
config_subclasses = [Test2, Test3, ...]  # 可通过自动化工具收集

# 动态创建 Union 类型
ConfigUnion = Union[tuple(config_subclasses)]

class Test1(BaseModel):
    test: Test
    config: ConfigUnion = Field(..., description="动态支持所有子类")

# 自动支持已注册的子类
create_test = Test1(
    test=test_instance,
    config=Test3(script="echo hello")  # 自动识别为 ConfigUnion
)


优点：无需手动维护 Union。  
缺点：类型检查较弱，需确保子类已注册。

方案 3：使用 Any + 自定义验证器

完全动态验证，但保留类型提示：
from typing import Any
from pydantic import validator

class Test1(BaseModel):
    test: Test
    config: Any = Field(..., description="动态支持 ConfigBase 的子类")

    @validator("config")
    def validate_config(cls, v):
        if not isinstance(v, ConfigBase) or type(v) is ConfigBase:
            raise ValueError("config 必须是 ConfigBase 的子类实例")
        return v  # 原样返回，保留子类所有字段


优点：完全灵活，支持任何子类。  
缺点：类型提示为 Any，IDE 支持较弱。

方案 4：Pydantic 的 Discriminated Union（区分不同子类）

通过字段值自动区分子类类型（需子类有唯一标识字段）：
from pydantic import Field, field_validator

class ConfigBase(BaseModel):
    model_type: str  # 所有子类必须包含此字段

class Test2(ConfigBase):
    model_type: str = "test2"
    sql: str

class Test3(ConfigBase):
    model_type: str = "test3"
    script: str

class Test1(BaseModel):
    test: Test
    config: ConfigBase = Field(..., discriminator="model_type")  # 自动识别子类


优点：自动解析子类，无需手动验证。  
缺点：需子类有统一标识字段。

最终推荐方案

根据需求选择：
1. 需要严格类型安全 → 方案 1（泛型）  
2. 子类动态注册 → 方案 2（动态 Union）  
3. 完全灵活 → 方案 3（Any + 验证器）  
4. 子类有共同标识字段 → 方案 4（Discriminated Union）

以 方案 1（泛型） 为例的完整代码：
from typing import TypeVar, Generic
from pydantic import BaseModel, Field

class ConfigBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

T = TypeVar('T', bound=ConfigBase)  # 关键：限定为 ConfigBase 的子类

class Test1(BaseModel, Generic[T]):
    test: Test
    config: T = Field(..., description="支持任意子类")

# 使用示例
test_instance = Test(run_cmd="default_cmd")
config_instance = Test3(script="echo hello")

create_test = Test1[Test3](  # 指定泛型类型
    test=test_instance,
    config=config_instance
)

print(create_test.model_dump_json(indent=2))

输出：
{
  "test": {
    "run_cmd": "default_cmd"
  },
  "config": {
    "script": "echo hello"
  }
}


总结

• 泛型 (TypeVar) 是最优解：平衡了类型安全和扩展性。  

• 避免直接使用 ConfigBase 作为字段类型，否则子类字段会被丢弃。  

• 根据项目需求选择方案，优先考虑 Pydantic 的原生支持（如泛型或 Discriminated Union）。
