from Lng.parser import parse
from Lng.ast import *

def test_simple():
	assert parse('1').getastlist() == [Number(1)]
	assert parse('hello').getastlist() == [Id('hello')]
	assert parse('\"String!\"').getastlist() == [String('\"String!\"')]

def test_assignment():
	assert parse('x = 4').getastlist() == [Assignment(Id('x'), Number(4))]

def test_binary_operation():
	assert parse('4 + 5').getastlist() == [Binary_Operation(Number(4),Number(5),('+'))]

def test_conditions():
	assert parse('x < 8').getastlist() == [Condition(Id('x'), ('<'), Number(8))]
	assert parse('x > y').getastlist() == [Condition(Id('x'), ('>'), Id('y'))]
	assert parse('5 <= 10').getastlist() == [Condition(Number(5), ('<='), Number(10))]
	assert parse('x >= y').getastlist() == [Condition(Id('x'), ('>='), Id('y'))]
	assert parse('x != y').getastlist() == [Condition(Id('x'), ('!='), Id('y'))]

def test_print():
	assert parse('print x').getastlist() == [Print(Id('x'))]
	assert parse('print 7').getastlist() == [Print(Number(7))]

def test_if():
	assert parse('if x < y { print 7 }').getastlist() == [
			If(Condition(Id('x'), ('<'), Id('y')), 
				Block([Print(Number(7))]), 
				None
				)
			]
	assert parse('if x < y { print 7 }else{print 9}').getastlist() == [
			If(
				Condition(Id('x'), ('<'), Id('y')), 
				Block([Print(Number(7))]), 
				Block([Print(Number(9))])
				)
			]

def test_return():
	assert parse('return x').getastlist() == [Return(Id('x'))]
	assert parse('return 0').getastlist() == [Return(Number(0))]

def test_while():
	assert parse('while x < y {print y}').getastlist() == [
		While(
			Condition(Id('x'), ('<'), Id('y')), 
			Block([Print(Id('y'))])
			)
		]

def test_function():
	assert parse('def func(){print n}').getastlist() == [
		Function(
			'func',
			None,
			Block([Print(Id('n'))])
			)
		]
	assert parse('def func(a){print n}').getastlist() == [
		Function(
			'func',
			Block([Id('a')]),
			Block([Print(Id('n'))])
			)
		]
	assert parse('def func(a b){print n}').getastlist() == [
		Function(
			'func',
			Block([Id('a'), Id('b')]),
			Block([Print(Id('n'))])
			)
		]

def test_calls():
	assert parse('x()').getastlist() == [
		Call(
			'x',
			None
			)
		]
	assert parse('x(a)').getastlist() == [
		Call(
			'x',
			Block([Id('a')])
			)
		]
	assert parse('x(a b)').getastlist() == [
		Call(
			'x',
			Block([Id('a'), Id('b')])
			)
		]

def test_class():
	assert parse('class x(){x = 5 def func(){print x}}').getastlist() == [
		Class(
			'x',
			Block([
				Assignment(Id('x'), Number(5)),
				Function(
					'func',
					None,
					Block([Print(Id('x'))])
					)
				])
			)
		]

def test_classop():
	assert parse('y.x').getastlist() == [
		ClassOp(
			'y',
			Id('x'),
			None, None, None
		)
	]
	assert parse('y.x()').getastlist() == [
		ClassOp(
			'y',
			None,
			'x',
			None, None
		)
	]
	assert parse('y.x(a)').getastlist() == [
		ClassOp(
			'y',
			None,
			'x',
			None, 
			Block([Id('a')])
		)
	]
	assert parse('y.x = 5').getastlist() == [
		ClassOp(
			'y',
			Id('x'),
			None,
			Number(5), None
		)
	]