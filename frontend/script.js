document.addEventListener('DOMContentLoaded', () => {
    const searchBtn = document.getElementById('search');
    const cancelBtn = document.getElementById('cancel');
    const addressInput = document.getElementById('address');
  
    // Handler for the search button: sends address data to the backend
    searchBtn.addEventListener('click', () => {
      const address = addressInput.value.trim();
  
      if (!address) {
        alert('Please enter an address.');
        return;
      }
  
      // Send the address data to a Python backend endpoint (adjust the URL as needed)
      fetch('/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ address })
      })
        .then(response => response.json())
        .then(data => {
          console.log('Python script response:', data);
          // Handle response data as needed
        })
        .catch(error => {
          console.error('Error sending address to Python script:', error);
        });
    });
  
    // Handler for the cancel button: clears the input field
    cancelBtn.addEventListener('click', () => {
      addressInput.value = '';
    });
  });