document.addEventListener('DOMContentLoaded', () => {
    const searchBtn = document.getElementById('search');
    const cancelBtn = document.getElementById('cancel');
    const addressInput = document.getElementById('address');
    const imageUpload = document.getElementById('imageUpload');
    const file = imageInput.files[0];
    const reader = new FileReader();

  
    // Handler for the search button: sends address data to the backend
    searchBtn.addEventListener('click', () => {
      const address = addressInput.value.trim();
      const image = imageUpload.value;

      if (!address || !imageUpload) {
        alert('Please enter one of the fields.');
        return;
      }
    
      if(adress){
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
}});

      if(file){
        reader.onloadend = async () => {
          const IMG = reader.result.split(',')[1];
        

        try {
          const response = await fetch('http://localhost:8000/identify-plant',{
            method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            image_data: base64Image
          }),
        });

        const results = await response.json();
        
        if (results.success) {
          resultBox.textContent = `Plant: ${results.plant.name}\n Info: ${results.plant.description || 'N/A'}`;
        } else {
          resultBox.textContent = `Error: ${results.message}`;
        }
      } catch (error) {
        resultBox.textContent = `Error: ${error.message}`;
      }
    };

    reader.readAsDataURL(file);

      }
      

    // Handler for the cancel button: clears the input field
    cancelBtn.addEventListener('click', () => {
      addressInput.value = '';
    });
  });
