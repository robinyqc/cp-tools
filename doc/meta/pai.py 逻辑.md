`pai.py` 逻辑

## 运行方式

`python pai.py src1 src2 gen [-c checker] [-t time_limit] [-m] [-g gen_args]` 或 `./pai.py ...`。

### 参数含义

+ `src1` 和 `src2` 是将要被检测的程序。
+ `gen` 是数据生成器。
+ `checker` 是输出检查器。
+ `time_limit` 是时间限制。
+ `-m` 表示制作源文件。
+ `gen_args` 是传送给 `gen` 的参数。

## 参数规则

+ `src1` 是一个文件名（不能是文件夹名，可以没有后缀名）。
+ `src2` 的规则同 `src1`。
+ `gen` 是一个文件名，通常是 `.py` 文件。
+ `checker` 是一个可选项，且是一个可执行文件或者 `.py` 文件。并且运行方式形如：`checker x.in x.out x.ans`。
+ `time_limit` 是一个可选项，它应当是一个数或者一个数紧随一个时间单位，比如 `1000` 或者 `1000ms` 或者 `1.0s`。默认为 `1s`。时间单位支持秒和毫秒。
+ `compile_command` 是一个可选项，并且可以有若干个参数。例如：`g++ src.cpp -o src`。

## 运行逻辑

### 初始化

1. 对于 `src1`, `src2`, `gen`, `checker`（如果存在）应用以下路径查找规则：
   + 若给定文件路径无歧义，那么什么也不做。否则若果当前路径下存在该文件，则使用该文件。否则在系统默认路径下查找文件。
2. 若存在 `-m` 标志，那么，用 make 命令制作 `src1`  和 `src2`。比如说 `src1 = 's.cpp'`，那么执行 `make s`。
3. 解析运行方式：将 `src1` 替换成 `src1` 的最佳运行方式（比如 `src1.py` 替换成 `python3 src1.py`，`src1` 为二进制可执行文件就什么都不做）。对 `src2` 和 `gen` 同理替换。如果 `checker` 存在，那么同理替换。
4. 若存在，解析 `time_limit`：当它是一个数字时，将其转为以毫秒为单位的时间，比如 `1000` --> `1000ms`。最后将时间单位转换为毫秒，比如 `1s` --> `1000ms`。

### 执行

1. 若当前路径下并没有 `pai_temp` 文件夹，那么创建。
2. 运行 `gen`（如果 `gen_args` 存在，则将 `gen_args`  传入 `gen`），捕获其标准输出到内存。如果内存不足，则将输出写入文件 `pai_temp/a.in`。
3. 运行 `src1` 和 `src2`，他们的输入是 `gen` 的输出 ，并且分别输出到 `pai_temp/a.out` 和 `pai_temp/a.ans`。忽略他们的标准错误输出（比如定向到 `/dev/null`，如果能跨平台更好）。
   + 若存在 `time_limit`，那么如果 `src1` 或 `src2` 其中任意一个程序运行时的**墙钟时间 (real time)** 超过了 `time_limit`，那么立刻杀死该进程，报告该程序超时，并且退出 `pai.py`。
   + 若运行时，返回值不是 0，那么报告那个程序 RE 以及返回值并且退出程序。
4. 若存在 `checker` 那么执行 `checker pai_temp/a.in pai_temp/a.out pai_temp/a.ans`。忽略 checker 的标准输出，捕捉 checker 的标准错误。若其返回值非零，那么报告错误，并且退出 `pai.py`。若不存在 `checker`  那么比较 `a.out a.ans` 是否相等（不要使用 `diff`），忽略行末空格，文末换行，如果不同，那么报告错误，并且退出。
5. 输出当前执行了多少次这条语句（格式：`Test case: i`），并且回到 1。