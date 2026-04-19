"""Python - valid code."""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Product:
    id: int
    name: str
    price: float = 0.0


class ProductRepository:
    def __init__(self) -> None:
        self.products: List[Product] = []

    def add(self, product: Product) -> None:
        self.products.append(product)

    def find_by_id(self, product_id: int) -> Optional[Product]:
        for product in self.products:
            if product.id == product_id:
                return product
        return None

    def list_all(self) -> List[Product]:
        return list(self.products)


def main() -> None:
    repo = ProductRepository()
    repo.add(Product(id=1, name="Widget", price=9.99))

    product = repo.find_by_id(1)
    if product:
        print(f"Found: {product.name} @ {product.price}")


if __name__ == "__main__":
    main()
