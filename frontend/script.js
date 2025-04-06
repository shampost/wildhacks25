document.addEventListener('DOMContentLoaded', () => {
  const searchBtn = document.getElementById('search');
  const cancelBtn = document.getElementById('cancel');
  const addressInput = document.getElementById('address');
  const imageUpload = document.getElementById('imageUpload');
  const resultBox = document.getElementById('resultBox'); // Optional: if you have an element to display results

  searchBtn.addEventListener('click', async () => {
    const address = addressInput.value.trim();
    // Get the file at the time of click
    const file = imageUpload.files[0];

    // If neither address nor image is provided, alert the user
    if (!address && !file) {
      alert('Please enter an address or upload an image.');
      return;
    }

    // Process address if provided
    if (address) {
      try {
        const response = await fetch('http://127.0.0.1:5200/get-satellite-image', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ address })
        });
        const data = await response.json();

        if (data.error) {
          alert(`Error: ${data.error}`);
          console.error('Debug info:', data.debug);
        } else {
          // Save the satellite image and coordinates in session storage
          sessionStorage.setItem('satelliteImage', data.image);
          sessionStorage.setItem('coordinates', JSON.stringify(data.coordinates));
          // Redirect to the results page
          window.location.href = 'results.html';
          return; // Exit after processing the address
        }
      } catch (error) {
        console.error('Error sending address to backend:', error);
        alert('An error occurred while processing your request.');
        return;
      }
    }

    // Process image if provided (and no address, or address processing is complete)
    if (file) {
      const reader = new FileReader();
      reader.onloadend = async () => {
        // Get the Base64 portion if needed, or use the whole data URL
        const IMG = reader.result.split(',')[1];

        try {
          const response = await fetch('http://localhost:3000/identify-plant', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              image_data: IMG
            }),
          });
          const results = await response.json();

          // Store the full data URL in session storage for the next page
          sessionStorage.setItem('uploadedImage', reader.result);

          if (results.success) {
            if (resultBox) {
              resultBox.textContent = `Plant: ${results.plant.name}\nInfo: ${results.plant.description || 'N/A'}`;
            }
          } else {
            if (resultBox) {
              resultBox.textContent = `Error: ${results.message}`;
            }
          }

          // Redirect to the plant description page
          window.location.href = 'plantDescription.html';
        } catch (error) {
          console.error('Error processing image:', error);
          if (resultBox) {
            resultBox.textContent = `Error: ${error.message}`;
          }
        }
      };
      reader.readAsDataURL(file);
    }
  });

  // Handler for the cancel button: clears the input fields
  cancelBtn.addEventListener('click', () => {
    addressInput.value = '';
    imageUpload.value = '';
  });
});