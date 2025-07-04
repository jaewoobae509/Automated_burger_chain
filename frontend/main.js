async function placeOrder() {
  const name = document.getElementById('name').value;
  const burger = document.getElementById('burger').value;

  const response = await fetch('http://127.0.0.1:5000/order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customer_name: name, item: burger })
  });

  const result = await response.json();
  alert(result.message);
}
