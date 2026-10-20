# 代码解读概念索引

概念 → AST 节点或规则 → 含义 → 课程链接 → 术语表链接。构建期解析为站点数据；`check_explain.py` 校验链接。

## 概念表

| 概念 id | 名称 | AST 节点或规则 | 含义 | 课程链接 | 术语表链接 |
| --- | --- | --- | --- | --- | --- |
| module | 模块 | Module | 一个 `.py` 文件即模块，顶层语句在导入时执行。 | [01 运行 Python](../课程/01-环境与工具/01-运行Python代码.md) | [术语表](../课程/附录/术语表.md) |
| docstring | 文档字符串 | Expr, Constant | 三引号字符串放在模块/函数/类首行，成为 `__doc__`。 | [01 语法骨架](../课程/02-基础语法与数据类型/01-语法骨架与变量.md) | [术语表](../课程/附录/术语表.md) |
| comment | 注释 | 规则 | `#` 到行尾为注释，解释器忽略。 | [01 语法骨架](../课程/02-基础语法与数据类型/01-语法骨架与变量.md) | [术语表](../课程/附录/术语表.md) |
| import-statement | import 语句 | Import | 导入整个模块，通过 `模块.名字` 访问。 | [01 模块与 import](../课程/05-模块与包/01-模块与import.md) | [术语表](../课程/附录/术语表.md) |
| from-import | from 导入 | ImportFrom | 从模块按名字导入，可直接使用符号。 | [01 模块与 import](../课程/05-模块与包/01-模块与import.md) | [术语表](../课程/附录/术语表.md) |
| assignment | 赋值 | Assign | 把对象绑定到名字，`=` 右侧先求值。 | [01 语法骨架](../课程/02-基础语法与数据类型/01-语法骨架与变量.md) | [术语表](../课程/附录/术语表.md) |
| annotated-assign | 带注解赋值 | AnnAssign | 变量名后 `: 类型` 再赋值，供静态检查。 | [01 类型注解基础](../课程/09-类型注解/01-类型注解基础.md) | [术语表](../课程/附录/术语表.md) |
| aug-assign | 增强赋值 | AugAssign | `+=` 等先运算再绑定回原名字。 | [01 语法骨架](../课程/02-基础语法与数据类型/01-语法骨架与变量.md) | [术语表](../课程/附录/术语表.md) |
| literal-constant | 字面量与 None | Constant | `None`、数字、字符串等不可变字面量。 | [02 数字布尔与 None](../课程/02-基础语法与数据类型/02-数字布尔与None.md) | [术语表](../课程/附录/术语表.md) |
| uppercase-constant | 全大写常量名 | 规则 | PEP 8 约定全大写表常量，语言不强制。 | [02 函数定义](../课程/03-控制流与函数/02-函数定义与调用.md) | [术语表](../课程/附录/术语表.md) |
| boolean-operator | 布尔运算 | BoolOp | `and`/`or`/`not` 组合条件，短路求值。 | [02 数字布尔与 None](../课程/02-基础语法与数据类型/02-数字布尔与None.md) | [术语表](../课程/附录/术语表.md) |
| comparison | 比较运算 | Compare | `==`、`!=`、大小比较，结果为布尔值。 | [01 条件与循环](../课程/03-控制流与函数/01-条件与循环.md) | [术语表](../课程/附录/术语表.md) |
| if-statement | if 分支 | If | 条件为真执行缩进块，可接 elif/else。 | [01 条件与循环](../课程/03-控制流与函数/01-条件与循环.md) | [术语表](../课程/附录/术语表.md) |
| for-loop | for 循环 | For | 遍历可迭代对象，每次绑定一个元素。 | [01 条件与循环](../课程/03-控制流与函数/01-条件与循环.md) | [术语表](../课程/附录/术语表.md) |
| while-loop | while 循环 | While | 条件为真重复执行，注意避免死循环。 | [01 条件与循环](../课程/03-控制流与函数/01-条件与循环.md) | [术语表](../课程/附录/术语表.md) |
| for-else | for-else | For | 循环未被 break 结束时执行 else 块。 | [01 条件与循环](../课程/03-控制流与函数/01-条件与循环.md) | [术语表](../课程/附录/术语表.md) |
| break-statement | break | Break | 立即结束最近一层循环。 | [01 条件与循环](../课程/03-控制流与函数/01-条件与循环.md) | [术语表](../课程/附录/术语表.md) |
| continue-statement | continue | Continue | 跳过本次循环剩余语句，进入下一轮。 | [01 条件与循环](../课程/03-控制流与函数/01-条件与循环.md) | [术语表](../课程/附录/术语表.md) |
| pass-statement | pass | Pass | 占位空语句，保持语法合法。 | [01 语法骨架](../课程/02-基础语法与数据类型/01-语法骨架与变量.md) | [术语表](../课程/附录/术语表.md) |
| function-def | 函数定义 | FunctionDef | `def` 创建可调用对象，可带参数与文档字符串。 | [02 函数定义与调用](../课程/03-控制流与函数/02-函数定义与调用.md) | [术语表](../课程/附录/术语表.md) |
| async-function-def | 异步函数 | AsyncFunctionDef | `async def` 定义协程函数，需 await 驱动。 | [01 协程与事件循环](../课程/19-asyncio/01-协程与事件循环.md) | [术语表](../课程/附录/术语表.md) |
| return-statement | return | Return | 结束函数并返回一个值（或 None）。 | [02 函数定义与调用](../课程/03-控制流与函数/02-函数定义与调用.md) | [术语表](../课程/附录/术语表.md) |
| lambda-expression | lambda | Lambda | 匿名单行函数，常用于短小回调。 | [04 作用域闭包与 lambda](../课程/03-控制流与函数/04-作用域闭包与lambda.md) | [术语表](../课程/附录/术语表.md) |
| keyword-argument | 关键字参数 | keyword | 调用时 `name=value`，顺序无关。 | [03 参数进阶与解包](../课程/03-控制流与函数/03-参数进阶与解包.md) | [术语表](../课程/附录/术语表.md) |
| starred-unpack | 星号解包 | Starred | `*args`、`**kwargs` 在定义或调用时展开序列/映射。 | [03 参数进阶与解包](../课程/03-控制流与函数/03-参数进阶与解包.md) | [术语表](../课程/附录/术语表.md) |
| function-as-value | 函数是一等公民 | 规则 | 函数对象可赋值、传参、放进容器。 | [02 函数定义与调用](../课程/03-控制流与函数/02-函数定义与调用.md) | [术语表](../课程/附录/术语表.md) |
| class-def | 类定义 | ClassDef | `class` 创建类型，实例通过方法共享行为。 | [01 类与实例](../课程/07-类与对象/01-类与实例.md) | [术语表](../课程/附录/术语表.md) |
| list-literal | 列表字面量 | List | 有序可变序列，`[]` 创建。 | [01 列表元组与切片](../课程/04-容器/01-列表元组与切片.md) | [术语表](../课程/附录/术语表.md) |
| tuple-literal | 元组字面量 | Tuple | 有序不可变序列，`( )` 创建。 | [01 列表元组与切片](../课程/04-容器/01-列表元组与切片.md) | [术语表](../课程/附录/术语表.md) |
| dict-literal | 字典字面量 | Dict | 键值映射，`{}` 创建。 | [02 字典](../课程/04-容器/02-字典.md) | [术语表](../课程/附录/术语表.md) |
| set-literal | 集合字面量 | Set | 无序不重复元素集合。 | [03 集合](../课程/04-容器/03-集合.md) | [术语表](../课程/附录/术语表.md) |
| subscript | 下标访问 | Subscript | `seq[i]` 或 `map[key]` 取元素。 | [02 字典](../课程/04-容器/02-字典.md) | [术语表](../课程/附录/术语表.md) |
| slice | 切片 | Slice | `start:stop:step` 截取序列视图。 | [01 列表元组与切片](../课程/04-容器/01-列表元组与切片.md) | [术语表](../课程/附录/术语表.md) |
| list-comprehension | 列表推导式 | ListComp | 紧凑构造列表的语法糖。 | [04 推导式与解包](../课程/04-容器/04-推导式与解包.md) | [术语表](../课程/附录/术语表.md) |
| dict-comprehension | 字典推导式 | DictComp | 从迭代生成 dict 的语法糖。 | [04 推导式与解包](../课程/04-容器/04-推导式与解包.md) | [术语表](../课程/附录/术语表.md) |
| set-comprehension | 集合推导式 | SetComp | 从迭代生成 set 的语法糖。 | [04 推导式与解包](../课程/04-容器/04-推导式与解包.md) | [术语表](../课程/附录/术语表.md) |
| generator-expression | 生成器表达式 | GeneratorExp | 惰性产生值，节省内存。 | [01 迭代器与生成器](../课程/10-读代码技巧/01-迭代器与生成器.md) | [术语表](../课程/附录/术语表.md) |
| f-string | f-string | JoinedStr, FormattedValue | 字符串前缀 `f`，花括号内嵌表达式。 | [04 f-string 与格式化](../课程/02-基础语法与数据类型/04-f-string与格式化.md) | [术语表](../课程/附录/术语表.md) |
| call-expression | 调用表达式 | Call | 函数或方法加括号执行，可传位置/关键字参数。 | [02 函数定义与调用](../课程/03-控制流与函数/02-函数定义与调用.md) | [术语表](../课程/附录/术语表.md) |
| attribute-access | 属性访问 | Attribute | `.` 取对象属性或绑定方法。 | [01 类与实例](../课程/07-类与对象/01-类与实例.md) | [术语表](../课程/附录/术语表.md) |
| list-append | list.append | 规则 | 在列表末尾原地追加元素。 | [01 列表元组与切片](../课程/04-容器/01-列表元组与切片.md) | [术语表](../课程/附录/术语表.md) |
| str-join | str.join | 规则 | 用分隔符把字符串 iterable 拼成一个 str。 | [03 字符串](../课程/02-基础语法与数据类型/03-字符串.md) | [术语表](../课程/附录/术语表.md) |
| name-reference | 名字引用 | Name | 读取或赋值时使用的标识符。 | [01 语法骨架](../课程/02-基础语法与数据类型/01-语法骨架与变量.md) | [术语表](../课程/附录/术语表.md) |
| binary-operator | 二元运算 | BinOp | `+ - * / // % **` 等对两个操作数运算。 | [02 数字布尔与 None](../课程/02-基础语法与数据类型/02-数字布尔与None.md) | [术语表](../课程/附录/术语表.md) |
| unary-operator | 一元运算 | UnaryOp | `-x`、`not x` 等对单个操作数运算。 | [02 数字布尔与 None](../课程/02-基础语法与数据类型/02-数字布尔与None.md) | [术语表](../课程/附录/术语表.md) |
| conditional-expression | 条件表达式 | IfExp | `a if cond else b` 单行二选一。 | [01 条件与循环](../课程/03-控制流与函数/01-条件与循环.md) | [术语表](../课程/附录/术语表.md) |
| walrus-operator | 海象运算符 | NamedExpr | `:=` 在表达式内赋值并返回值。 | [04 推导式与解包](../课程/04-容器/04-推导式与解包.md) | [术语表](../课程/附录/术语表.md) |
| try-statement | try 语句 | Try | 捕获异常，配合 except/else/finally。 | [02 try-except-raise](../课程/06-异常/02-try-except-raise.md) | [术语表](../课程/附录/术语表.md) |
| except-handler | except 子句 | ExceptHandler | 匹配异常类型并处理。 | [02 try-except-raise](../课程/06-异常/02-try-except-raise.md) | [术语表](../课程/附录/术语表.md) |
| raise-statement | raise | Raise | 主动抛出异常，可带 from 链。 | [02 try-except-raise](../课程/06-异常/02-try-except-raise.md) | [术语表](../课程/附录/术语表.md) |
| assert-statement | assert | Assert | 条件为假时抛 AssertionError，常用于测试。 | [01 pytest 基础](../课程/15-测试/01-pytest基础.md) | [术语表](../课程/附录/术语表.md) |
| with-statement | with 语句 | With | 上下文管理器自动 setup/cleanup。 | [03 with 与上下文管理器](../课程/06-异常/03-with与上下文管理器.md) | [术语表](../课程/附录/术语表.md) |
| global-statement | global | Global | 声明函数内名字指模块全局变量。 | [04 作用域闭包与 lambda](../课程/03-控制流与函数/04-作用域闭包与lambda.md) | [术语表](../课程/附录/术语表.md) |
| nonlocal-statement | nonlocal | Nonlocal | 声明名字来自外层（非全局）函数。 | [04 作用域闭包与 lambda](../课程/03-控制流与函数/04-作用域闭包与lambda.md) | [术语表](../课程/附录/术语表.md) |
| del-statement | del | Delete | 删除名字绑定或容器元素。 | [01 语法骨架](../课程/02-基础语法与数据类型/01-语法骨架与变量.md) | [术语表](../课程/附录/术语表.md) |
| match-statement | match 语句 | Match | 结构化模式匹配，Python 3.10+。 | [04 match 语句](../课程/13-函数式与进阶语法/04-match语句.md) | [术语表](../课程/附录/术语表.md) |
| match-case | match case | match_case, MatchAs, MatchClass, MatchMapping, MatchOr, MatchSequence, MatchStar, MatchValue | match 分支及其子模式节点。 | [04 match 语句](../课程/13-函数式与进阶语法/04-match语句.md) | [术语表](../课程/附录/术语表.md) |
| with-item | with 子句 | withitem | `with A() as x` 中的上下文管理器项。 | [03 with](../课程/06-异常/03-with与上下文管理器.md) | [术语表](../课程/附录/术语表.md) |
| await-expression | await | Await | 在协程内等待异步结果。 | [01 协程与事件循环](../课程/19-asyncio/01-协程与事件循环.md) | [术语表](../课程/附录/术语表.md) |
| yield-expression | yield | Yield | 生成器产出值并暂停。 | [01 迭代器与生成器](../课程/10-读代码技巧/01-迭代器与生成器.md) | [术语表](../课程/附录/术语表.md) |
| yield-from | yield from | YieldFrom | 委托子生成器产出。 | [01 迭代器与生成器](../课程/10-读代码技巧/01-迭代器与生成器.md) | [术语表](../课程/附录/术语表.md) |
| async-for | 异步 for | AsyncFor | 异步迭代 async iterable。 | [01 协程与事件循环](../课程/19-asyncio/01-协程与事件循环.md) | [术语表](../课程/附录/术语表.md) |
| decorator-call | 装饰器 | Call, FunctionDef | `@deco` 等价于函数定义后包装赋值。 | [02 装饰器](../课程/10-读代码技巧/02-装饰器.md) | [术语表](../课程/附录/术语表.md) |
| main-guard | main 入口 | If, Compare | `if __name__ == "__main__":` 仅脚本直接运行时执行。 | [01 运行 Python](../课程/01-环境与工具/01-运行Python代码.md) | [术语表](../课程/附录/术语表.md) |
| type-hint | 类型注解 | AnnAssign, arg, TypeAlias, TypeVar | 标注参数与返回值类型，或声明 TypeAlias/TypeVar。 | [01 类型注解基础](../课程/09-类型注解/01-类型注解基础.md) | [术语表](../课程/附录/术语表.md) |
| pathlib-usage | pathlib | Attribute, Call | 面向对象的路径操作，替代部分 os.path。 | [01 pathlib 与文件](../课程/08-常用标准库/01-pathlib与文件.md) | [术语表](../课程/附录/术语表.md) |
| json-loads | JSON 解析 | Call | `json.loads/dumps` 在 str 与 Python 对象间转换。 | [02 json](../课程/08-常用标准库/02-json.md) | [术语表](../课程/附录/术语表.md) |
| env-getenv | 环境变量 | Call, Attribute | `os.getenv` 读取进程环境变量。 | [03 os-sys 与环境变量](../课程/08-常用标准库/03-os-sys与环境变量.md) | [术语表](../课程/附录/术语表.md) |
| pytest-test | pytest 测试 | FunctionDef | 以 `test_` 开头的函数会被 pytest 收集。 | [01 pytest 基础](../课程/15-测试/01-pytest基础.md) | [术语表](../课程/附录/术语表.md) |
| dataclass-decorator | dataclass | ClassDef, Call | `@dataclass` 自动生成 __init__ 等方法。 | [03 dataclass 与枚举](../课程/07-类与对象/03-dataclass与枚举.md) | [术语表](../课程/附录/术语表.md) |
| enum-class | 枚举 | ClassDef | Enum 子类表示有限常量集。 | [03 dataclass 与枚举](../课程/07-类与对象/03-dataclass与枚举.md) | [术语表](../课程/附录/术语表.md) |
| protocol-typing | Protocol | ClassDef | 结构化子类型，描述鸭子类型接口。 | [04 ABC 与 Protocol](../课程/12-数据模型与协议/04-ABC与Protocol.md) | [术语表](../课程/附录/术语表.md) |
| special-dunder | 特殊方法 | FunctionDef | `__init__`、`__str__` 等双下划线协议方法。 | [01 特殊方法全景](../课程/12-数据模型与协议/01-特殊方法全景.md) | [术语表](../课程/附录/术语表.md) |
| agent-tool-call | Agent 工具调用 | Call, Dict | 模型返回工具名与参数，本地函数执行。 | [01 工具调用协议](../课程/23-Agent实战/01-工具调用协议.md) | [术语表](../课程/附录/术语表.md) |

## 易错点（与 py-explain 规则 id 对齐）

| 规则 id | 说明 | Ruff | 课程 |
| --- | --- | --- | --- |
| mutable-default-arg | 可变默认参数 | B006 | [03 参数进阶](../课程/03-控制流与函数/03-参数进阶与解包.md) |
| is-literal-compare | is 比较字面量 | E712 | [01 条件与循环](../课程/03-控制流与函数/01-条件与循环.md) |
| bare-except | 裸 except | E722 | [02 try-except](../课程/06-异常/02-try-except-raise.md) |
| none-equality | == 与 None | E711 | [02 数字布尔与 None](../课程/02-基础语法与数据类型/02-数字布尔与None.md) |
| wildcard-import | import * | F403 | [01 模块与 import](../课程/05-模块与包/01-模块与import.md) |
| open-no-with | open 无 with | SIM115 | [03 with](../课程/06-异常/03-with与上下文管理器.md) |
| shadow-builtin | 遮蔽内置名 | A001 | [02 函数定义](../课程/03-控制流与函数/02-函数定义与调用.md) |
| mutable-class-attribute | 类级可变对象 | B006 | [01 类与实例](../课程/07-类与对象/01-类与实例.md) |
| except-pass | except: pass | S110 | [02 try-except](../课程/06-异常/02-try-except-raise.md) |
| assert-trivial | assert True | B011 | [01 pytest 基础](../课程/15-测试/01-pytest基础.md) |
| len-as-bool | if len(x) | PLC1802 | [01 列表](../课程/04-容器/01-列表元组与切片.md) |
| duplicate-key-dict-literal | dict 重复键 | F601 | [02 字典](../课程/04-容器/02-字典.md) |
