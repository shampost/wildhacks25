document.addEventListener('DOMContentLoaded', () => {
  const searchBtn = document.getElementById('search');
  const cancelBtn = document.getElementById('cancel');
  const addressInput = document.getElementById('address');

  if (searchBtn) {
    searchBtn.addEventListener('click', () => {
      const address = addressInput.value.trim();
      if (!address) {
        alert('Please enter an address.');
        return;
      }
      fetch('http://127.0.0.1:5200/get-satellite-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ address })
      })
        .then(response => response.json())
        .then(data => {
          if (data.error) {
            alert(`Error: ${data.error}`);
            console.error('Debug info:', data.debug);
          } else {
            // Save the base64 image and coordinates in session storage
            sessionStorage.setItem('satelliteImage', data.image);
            sessionStorage.setItem('coordinates', JSON.stringify(data.coordinates));
            // Redirect to the results page (update the filename if needed)
            window.location.href = 'results.html';
          }
        })
        .catch(error => {
          console.error('Error sending address to backend:', error);
          alert('An error occurred while processing your request.');
        });
    });

    cancelBtn.addEventListener('click', () => {
      addressInput.value = '';
    });
  }
});