from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, declarative_base

engine = create_engine('sqlite:///banco.db')
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


# =======================
# MODELO USUÁRIO
# =======================
class Usuario(Base):
    __tablename__ = 'usuarios'

    id_usuario = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)
    email = Column(String(80), nullable=False, unique=True)
    senha = Column(String(120), nullable=False)

    def save(self):
        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session.delete(self)
        db_session.commit()

    def serialize(self):
        return {
            "id_usuario": self.id_usuario,
            "nome": self.nome,
            "email": self.email
        }

    def __repr__(self):
        return f"<Usuario id={self.id_usuario} nome='{self.nome}' email='{self.email}'>"


# =======================
# MODELO PRODUTO
# =======================
class Produto(Base):
    __tablename__ = 'produtos'

    id_produto = Column(Integer, primary_key=True)
    nome = Column(String(80), nullable=False)
    preco = Column(Float, nullable=False)
    categoria = Column(String(40))
    quantidade = Column(Integer, default=0)

    estoque = relationship("Estoque", back_populates="produto")

    def save(self):
        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session.delete(self)
        db_session.commit()

    def serialize(self):
        return {
            "id_produto": self.id_produto,
            "nome": self.nome,
            "preco": self.preco,
            "categoria": self.categoria,
            "quantidade": self.quantidade
        }

    def __repr__(self):
        return (
            f"<Produto id={self.id_produto} nome='{self.nome}' preco={self.preco} "
            f"categoria='{self.categoria}' quantidade={self.quantidade}>"
        )


# =======================
# MODELO ESTOQUE
# =======================
class Estoque(Base):
    __tablename__ = 'estoque'

    id_estoque = Column(Integer, primary_key=True)
    id_produto = Column(Integer, ForeignKey('produtos.id_produto'))
    quantidade_movimentada = Column(Integer, nullable=False)
    status = Column(String(10), nullable=False)  # entrada / saída

    produto = relationship("Produto", back_populates="estoque")

    def save(self):
        # altera o estoque automaticamente
        if self.status == "entrada":
            self.produto.quantidade += self.quantidade_movimentada
        elif self.status == "saida":
            self.produto.quantidade -= self.quantidade_movimentada

        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session.delete(self)
        db_session.commit()

    def serialize(self):
        return {
            "id_estoque": self.id_estoque,
            "id_produto": self.id_produto,
            "quantidade_movimentada": self.quantidade_movimentada,
            "status": self.status
        }

    def __repr__(self):
        return (
            f"<Estoque id={self.id_estoque} produto={self.id_produto} "
            f"qtd={self.quantidade_movimentada} status='{self.status}'>"
        )


# =======================
# INICIALIZAR BANCO
# =======================
def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    init_db()
