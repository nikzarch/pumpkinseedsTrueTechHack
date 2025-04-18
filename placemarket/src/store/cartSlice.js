import { createSlice } from "@reduxjs/toolkit";

const cartSlice = createSlice({
  name: "cart",
  initialState: {},
  reducers: {
    addToCart: (state, action) => {
      const id = action.payload.recordId;
      if (!state[id]) {
        state[id] = { ...action.payload, quantity: 1 };
      } else {
        state[id].quantity += 1;
      }
    },
    removeFromCart: (state, action) => {
      delete state[action.payload];
    },
    changeQuantity: (state, action) => {
      const { id, delta } = action.payload;
      if (!state[id]) return;
      const newQty = state[id].quantity + delta;
      if (newQty <= 0) delete state[id];
      else state[id].quantity = newQty;
    },
    clearCart: () => ({}),
  },
});

export const { addToCart, removeFromCart, changeQuantity, clearCart } = cartSlice.actions;
export default cartSlice.reducer;
