// server.js
const express = require('express');
const app = express();
const cors = require('cors');
const bodyParser = require('body-parser');
const cors = require('cors');
app.use(cors());

app.use(cors());
app.use(bodyParser.json());

// Mock user credentials (replace with your own authentication logic)
const validCredentials = {
  username: 'valid_user',
  password: 'valid_password',
};

app.post('/validate-credentials', (req, res) => {
  const { username, password } = req.body;
  if (username === validCredentials.username && password === validCredentials.password) {
    res.status(200).json({ message: 'Credentials are valid' });
  } else {
    res.status(401).json({ message: 'Invalid credentials' });
  }
});

app.listen(3001, () => {
  console.log('Server is running on port 3001');
});
