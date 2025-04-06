document.addEventListener('DOMContentLoaded', () => {
  const searchBtn = document.getElementById('search');
  const cancelBtn = document.getElementById('cancel');
  const addressInput = document.getElementById('address');

  if (searchBtn) {
    // Handle the "Search" button click
    searchBtn.addEventListener('click', () => {
      const address = addressInput.value.trim();
      if (!address) {
        alert('Please enter an address.');
        return;
      }

      // Send the address to your Flask backend
      fetch('http://127.0.0.1:5200/get-satellite-image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address })
      })
        .then(response => response.json())
        .then(data => {
          if (data.error) {
            alert(`Error: ${data.error}`);
            console.error('Debug info:', data.debug);
          } else {
            console.log("Backend response:", data); // Debug log
            // Save relevant data in sessionStorage
            sessionStorage.setItem('satelliteImage', data.image);
            sessionStorage.setItem('coordinates', JSON.stringify(data.coordinates));
            sessionStorage.setItem('geminiRawOutput', data.geminiRaw || '');
            // Save the plants array
            sessionStorage.setItem('geminiPlants', JSON.stringify(data.plants || []));
            
            // Redirect to the results page
            window.location.href = 'results.html';
          }
        })
        .catch(error => {
          console.error('Error sending address to backend:', error);
          alert('An error occurred while processing your request.');
        });
    });

    // Handle the "Cancel" button click
    if (cancelBtn) {
      cancelBtn.addEventListener('click', () => {
        addressInput.value = '';
      });
    }
  }
});