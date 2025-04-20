import React, { useState } from "react";
import { useDispatch } from "react-redux";
import { addToCart } from "../store/cartSlice";
import "../style/ProductCard.css";
import { API_TOKEN } from "../components/App.jsx";

const QUESTION_API_URL = import.meta.env.VITE_API_QUESTION_URL;

export default function ProductCard({ product }) {
  const dispatch = useDispatch();
  const fields = product.fields;

  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [link, setLink] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    const data = {
      records: [
        {
          fields: {
            "Сообщение": message,
            "Имя покупателя": name,
            "Ссылка на покупателя": link,
            "Артикул товара": [product.recordId],
            "Статус": "Создан",
          },
        },
      ],
      fieldKey: "name",
    };

    try {
      const response = await fetch(QUESTION_API_URL, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${API_TOKEN}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      console.log(JSON.stringify(data))
      if (response.ok) {
        console.log(response)
        setName("");
        setLink("");
        setMessage("");
        setShowForm(false);
      } else {
        const result = await response.json();
        console.error("Ошибка отправки вопроса:", result);
      }
    } catch (error) {
      console.error("Ошибка при отправке данных:", error);
    }
  };

  return (
    <div className="product-card">
      <h2 className="product-title">{fields["Название товара"]}</h2>
      <p>Цена: {fields["Цена"]}₽</p>
      <button onClick={() => dispatch(addToCart(product))} className="add-button">
        В корзину
      </button>
      <button onClick={() => setShowForm(!showForm)} className="question-button">
        Задать вопрос по товару
      </button>

      {showForm && (
        <form onSubmit={handleSubmit} className="question-form">
          <input
            type="text"
            placeholder="Ваше имя"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Ссылка на ваш контакт"
            value={link}
            onChange={(e) => setLink(e.target.value)}
            required
          />
          <textarea
            placeholder="Ваш вопрос"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            required
          />
          <button type="submit">Отправить</button>
        </form>
      )}
    </div>
  );
}
