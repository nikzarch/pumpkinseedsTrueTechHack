import React, { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { addToCart } from "../store/cartSlice";
import "../style/ProductCard.css";
import { API_TOKEN } from "../components/App.jsx";

export default function ProductCard({ product }) {
  const dispatch = useDispatch();
  const fields = product.fields;
  //const imagePath = fields.Фото?.[0]?.url;

  //const [imageSrc, setImageSrc] = useState(null);

  // useEffect(() => {
  //   if (imagePath) {
  //     fetch("https://true.tabs.sale" + imagePath, {
  //       headers: {
  //         Authorization: `Bearer ${API_TOKEN}`,
  //       },
  //     })
  //       .then((res) => res.blob())
  //       .then((blob) => {
  //         const objectURL = URL.createObjectURL(blob);
  //         setImageSrc(objectURL);
  //       })
  //       .catch((err) => {
  //         console.error("Ошибка загрузки изображения", err);
  //       });
  //   }
  // }, [imagePath]); // CORS prohibited to fetch images:(

  return (
    <div className="product-card">
      {/* {imageSrc && (
        <img
          src={imageSrc}
          alt={fields["Название товара"]}
          className="product-image"
        />
      )} */}
      <h2 className="product-title">{fields["Название товара"]}</h2>
      <p>Цена: {fields["Цена"]}₽</p>
      <button
        onClick={() => dispatch(addToCart(product))}
        className="add-button"
      >
        В корзину
      </button>
    </div>
  );
}
