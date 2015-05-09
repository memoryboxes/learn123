notes for reading [Expert Python Programming] -- by Tarek Ziade

## notes

#### 2.1
Python风格的语法意味着什么?
Python风格的语法是一种对小代码模式最有效的语法。这个词也已用于注入程序库这样的高级别事物上。在那种情况下，如果程序库能够很好地使用Python的风格，它就被认为是Python化(*Phthonic*)的。在开发社群中，这个术语有时用来对代码块进行分类。

#### 2.2
PEP的含义是Python增强建议(*Python Enhancement Proposal*)。它是在Python上进行修改的文件，也是开发社团讨论的一个出发点。
参见:
http://www.python.org/dev/peps/pep-0001

*生成器*:当需要一个将返回一个序列或在循环中执行的函数时，应该考虑使用生成器。

保持代码简单，而不是数据:拥有许多简单的处理序列值得可迭代函数，要比一个复杂的、每次计算一个值得函数更好一些。
