# -*- coding: utf-8 -*-
from tinySelf.vm.debug.pretty_print_ast import pretty_print_ast


def test_pretty_print_ast():
    source = """Send(obj=Object(slots={test_while_100: Object(slots={i: \
IntNumber(0), i:: AssignmentPrimitive()}, code=[Send(obj=Block(code=[Send(obj=\
Send(obj=Self(), msg=Message(i)), msg=BinaryMessage(name=<, parameter=IntNumber\
(1)))]), msg=KeywordMessage(name=whileTrue:, parameters=[Block(code=[Send(obj=\
Self(), msg=KeywordMessage(name=i:, parameters=[Send(obj=Send(obj=Self(), \
msg=Message(i)), msg=BinaryMessage(name=+, parameter=IntNumber(1)))])), \
Send(obj=Self(), msg=Message(false))])])), Send(obj=Send(obj=Send(obj=Self(), \
msg=Message(i)), msg=Message(asString)), msg=Message(printLine))]), test_another: \
Object(slots={x: Nil(), x:: AssignmentPrimitive(), brekeke: Nil(), brekeke:: \
AssignmentPrimitive()}, code=[Send(obj=Self(), msg=KeywordMessage(name=x:, \
parameters=[IntNumber(0)])), Send(obj='another', msg=Message(printLine)), \
Send(obj=Self(), msg=Message(brekeke)), Send(obj=Block(code=[Send(obj=Send(obj=\
Self(), msg=Message(x)), msg=BinaryMessage(name=<, parameter=IntNumber(2)))]), \
msg=KeywordMessage(name=whileTrue:, parameters=[Block(code=[Send(obj=Self(), \
msg=KeywordMessage(name=x:, parameters=[Send(obj=Send(obj=Self(), msg=Message(x)), \
msg=BinaryMessage(name=+, parameter=IntNumber(1)))])), Send(obj=Self(), \
msg=Message(nil))])])), Send(obj=Send(obj=Send(obj=Self(), msg=Message(x)), \
msg=Message(asString)), msg=Message(printLine))]), test_while: \
Object(code=[Send(obj=Self(), msg=Message(test_while_100)), Send(obj=Self(), \
msg=Message(test_another))])}), msg=Message(test_while))"""

    assert pretty_print_ast(source) == """Send(
  obj=Object(
    slots={
      test_while_100: Object(
        slots={
          i: IntNumber(0),
          i:: AssignmentPrimitive()
        },
        code=[
          Send(
            obj=Block(
              code=[
                Send(
                  obj=Send(
                    obj=Self(),
                    msg=Message(i)
                  ),
                  msg=BinaryMessage(
                    name=<,
                    parameter=IntNumber(1)
                  )
                )
              ]
            ),
            msg=KeywordMessage(
              name=whileTrue:,
              parameters=[
                Block(
                  code=[
                    Send(
                      obj=Self(),
                      msg=KeywordMessage(
                        name=i:,
                        parameters=[
                          Send(
                            obj=Send(
                              obj=Self(),
                              msg=Message(i)
                            ),
                            msg=BinaryMessage(
                              name=+,
                              parameter=IntNumber(1)
                            )
                          )
                        ]
                      )
                    ),
                    Send(
                      obj=Self(),
                      msg=Message(false)
                    )
                  ]
                )
              ]
            )
          ),
          Send(
            obj=Send(
              obj=Send(
                obj=Self(),
                msg=Message(i)
              ),
              msg=Message(asString)
            ),
            msg=Message(printLine)
          )
        ]
      ),
      test_another: Object(
        slots={
          x: Nil(),
          x:: AssignmentPrimitive(),
          brekeke: Nil(),
          brekeke:: AssignmentPrimitive()
        },
        code=[
          Send(
            obj=Self(),
            msg=KeywordMessage(
              name=x:,
              parameters=[
                IntNumber(0)
              ]
            )
          ),
          Send(
            obj='another',
            msg=Message(printLine)
          ),
          Send(
            obj=Self(),
            msg=Message(brekeke)
          ),
          Send(
            obj=Block(
              code=[
                Send(
                  obj=Send(
                    obj=Self(),
                    msg=Message(x)
                  ),
                  msg=BinaryMessage(
                    name=<,
                    parameter=IntNumber(2)
                  )
                )
              ]
            ),
            msg=KeywordMessage(
              name=whileTrue:,
              parameters=[
                Block(
                  code=[
                    Send(
                      obj=Self(),
                      msg=KeywordMessage(
                        name=x:,
                        parameters=[
                          Send(
                            obj=Send(
                              obj=Self(),
                              msg=Message(x)
                            ),
                            msg=BinaryMessage(
                              name=+,
                              parameter=IntNumber(1)
                            )
                          )
                        ]
                      )
                    ),
                    Send(
                      obj=Self(),
                      msg=Message(nil)
                    )
                  ]
                )
              ]
            )
          ),
          Send(
            obj=Send(
              obj=Send(
                obj=Self(),
                msg=Message(x)
              ),
              msg=Message(asString)
            ),
            msg=Message(printLine)
          )
        ]
      ),
      test_while: Object(
        code=[
          Send(
            obj=Self(),
            msg=Message(test_while_100)
          ),
          Send(
            obj=Self(),
            msg=Message(test_another)
          )
        ]
      )
    }
  ),
  msg=Message(test_while)
)"""