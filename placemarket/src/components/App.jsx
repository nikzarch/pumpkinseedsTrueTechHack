import { useEffect, useState } from "react";
import ProductGrid from "./ProductGrid";
import Cart from "./Cart";
import '../style/App.css';
const API_GET_URL = import.meta.env.VITE_API_GET_URL;
export const API_TOKEN = import.meta.env.VITE_API_TOKEN;
export default function App() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch(API_GET_URL, {
      headers: { Authorization: `Bearer ${API_TOKEN}` },
    })
      .then((result) => result.json())
      .then((data) => {
        console.log("полученные данные:", data);
        setProducts(data.data.records);
      })
      .catch((err) =>
        console.error("Ошибка загрузки доступных товаров", err)
      );
  }, []);

  return (
    <div className="app-container">
      <header className="app-header">
        Плейсмаркет Дикая Черешня
        
        <a
          href="https://true.tabs.sale/share/shrEFLtBBctPzPPwnaLzx"
          className="feedback-button"
          style={{
            backgroundColor: '#fff',
            color: '#064e3b',
            padding: '6px 12px',
            borderRadius: '6px',
            fontWeight: 'bold',
            textDecoration: 'none',
            border: '2px solid #fff',
            marginLeft: 'auto'
          }}
        >
          Оставить обратную связь
        </a>
      </header>

      <main className="product-grid-container">
        <ProductGrid products={products} />
      </main>
      <Cart />
    </div>
  )

}


