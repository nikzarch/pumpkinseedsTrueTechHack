import { useSelector, useDispatch } from "react-redux";
import { changeQuantity, removeFromCart, clearCart } from "../store/cartSlice";
import "../style/Cart.css";
import { API_TOKEN } from "../components/App.jsx";

const API_POST_URL = import.meta.env.VITE_API_POST_URL;

export default function Cart() {
  const cart = useSelector((state) => state.cart);
  const dispatch = useDispatch();
  const items = Object.values(cart);
  const total = items.reduce((sum, item) => sum + item.fields["Цена"] * item.quantity, 0);

  const sendCart = async () => {
    const records = items.map((item) => ({
      fields: {
        Название: item.fields["Название товара"], 
        "SKU (ID товара)": item.fields["SKU (ID товара)"], 
        Маркетплейс: "дикая черешня",
        Количество : item.quantity,
      },
    }));

    const data = {
      records: records,
      fieldKey: "name",
    };

    try {
      const response = await fetch(API_POST_URL, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${API_TOKEN}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();
      if (response.ok) {
        console.log("Заказ успешно отправлен:", result);

        dispatch(clearCart());
      } else {
        console.error("Ошибка отправки заказа:", result);
      }
    } catch (error) {
      console.error("Ошибка при отправке данных на сервер:", error);
    }
  };

  return (
    <aside className="cart">
      <h2>Корзина</h2>
      {items.length === 0 ? (
        <p>Корзина пуста</p>
      ) : (
        <ul>
          {items.map((item) => (
            <li key={item.recordId} className="cart-item">
              <span>{item.fields["Название товара"]}</span>
              <span>{item.fields["Цена"]}₽ x {item.quantity}</span>
              <div>
                <button onClick={() => dispatch(changeQuantity({ id: item.recordId, delta: -1 }))}>−</button>
                <button onClick={() => dispatch(changeQuantity({ id: item.recordId, delta: 1 }))}>+</button>
                <button onClick={() => dispatch(removeFromCart(item.recordId))}>Удалить</button>
              </div>
            </li>
          ))}
        </ul>
      )}
      <p>Итого: {total}₽</p>
      {items.length > 0 && <button onClick={() => dispatch(clearCart())}>Очистить корзину</button>}
      {items.length > 0 && (
        <button onClick={sendCart}>Приобрести</button>
      )}
    </aside>
  );
}
