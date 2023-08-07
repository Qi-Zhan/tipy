from .ast import *


class Visitor:
    pass


class AstVisitor(Visitor):
    def visit_program(self, node: Program):
        for func in node.functions:
            func.accept(self)

    def visit_function(self, node: Function):
        node.name.accept(self)
        node.parameters.accept(self)
        node.body.accept(self)

    def visit_funblock(self, node: FunBlock):
        for varstmt in node.varstmts:
            varstmt.accept(self)
        for stmt in node.stmts:
            stmt.accept(self)
        if node.returnstmt is not None:
            node.returnstmt.accept(self)

    def visit_vardecl(self, node: Vardecl):
        for name in node.ids:
            name.accept(self)

    def visit_id(self, node: Id):
        pass

    def visit_const(self, node: Const):
        pass

    def visit_error(self, node: Error):
        node.value.accept(self)

    def visit_binary_expr(self, node: BinaryExpr):
        node.left.accept(self)
        node.right.accept(self)

    def visit_unary_expr(self, node: UnaryExpr):
        node.expr.accept(self)

    def visit_call(self, node: Call):
        node.name.accept(self)
        for arg in node.args:
            arg.accept(self)

    def visit_return(self, node: Return):
        node.expr.accept(self)

    def visit_if(self, node: If):
        node.cond.accept(self)
        node.then.accept(self)
        if node.else_ is not None:
            node.else_ .accept(self)

    def visit_while(self, node: While):
        node.cond.accept(self)
        node.then.accept(self)

    def visit_reference(self, node: Reference):
        node.name.accept(self)

    def visit_deref(self, node: Deref):
        node.expr.accept(self)

    def visit_assign(self, node: Assign):
        node.name.accept(self)
        node.expr.accept(self)

    def visit_alloc(self, node: Alloc):
        node.expr.accept(self)

    def visit_direct_field_write(self, node: DirectFieldWrite):
        node.name.accept(self)
        node.field.accept(self)
    
    def visit_input(self, node: Input):
        pass

    def visit_indirect_field_write(self, node: IndirectFieldWrite):
        node.expr.accept(self)
        node.field.accept(self)

    def visit_deref_write(self, node: DerefWrite):
        node.expr.accept(self)

    def visit_record(self, node: Record):
        for field in node.fields:
            field[0].accept(self)
            field[1].accept(self)

    def visit_access(self, node: Access):
        node.name.accept(self)
        for field in node.fields:
            field.accept(self)

    def visit_parameters(self, node: Parameters):
        for param in node.params:
            param.accept(self)

    def visit_block(self, node: Block):
        for stmt in node.stmts:
            stmt.accept(self)

    def visit_output(self, node: Output):
        node.expr.accept(self)

class CFGVisitor(Visitor):
    pass
