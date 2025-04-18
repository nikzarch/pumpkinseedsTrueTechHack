import React from "react";
import ProductCard from "./ProductCard";
import "../style/ProductGrid.css";

export default function ProductGrid({ products }) {
    if (!products || !Array.isArray(products)) {
      return <p>Загрузка товаров...</p>;
    }
  
    return (
      <div className="product-grid">
        {products.map((product) => (
          <ProductCard key={product.recordId} product={product} />
        ))}
      </div>
    );
  }
  
