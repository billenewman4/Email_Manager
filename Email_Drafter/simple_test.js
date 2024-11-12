async function generateEmail() {
    try {
        // Show loading state
        const loadingElement = document.getElementById('loading');
        const resultElement = document.getElementById('result');
        if (loadingElement) loadingElement.style.display = 'block';
        if (resultElement) resultElement.innerHTML = '';

        // Make API call
        const response = await fetch('http://localhost:8000/generate-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Display the result
        if (resultElement) {
            resultElement.innerHTML = `
                <h3>Generated Email:</h3>
                <pre>${data.email_draft}</pre>
            `;
        }

    } catch (error) {
        console.error('Error:', error);
        if (document.getElementById('result')) {
            document.getElementById('result').innerHTML = `
                <div class="error">
                    Error generating email: ${error.message}
                </div>
            `;
        }
    } finally {
        // Hide loading state
        if (document.getElementById('loading')) {
            document.getElementById('loading').style.display = 'none';
        }
    }
}

// Example HTML to use with this JavaScript:
/*
<!DOCTYPE html>
<html>
<head>
    <title>Email Generator</title>
    <style>
        .error { color: red; }
        #loading { display: none; }
        pre { white-space: pre-wrap; }
    </style>
</head>
<body>
    <button onclick="generateEmail()">Generate Email</button>
    <div id="loading">Generating email...</div>
    <div id="result"></div>
    <script src="email_client.js"></script>
</body>
</html>
*/