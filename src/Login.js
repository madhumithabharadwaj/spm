import React, { Component } from 'react';
import { Container, TextField, Button, Box, InputLabel } from '@mui/material';

class Login extends Component {
  constructor() {
    super();
    this.state = {
      username: '',
      password: '',
      error: '',
    };
  }

  handleChange = (e) => {
    this.setState({
      [e.target.name]: e.target.value,
    });
  }

  handleGitHubLogin = (e) => {
    e.preventDefault();
    const clientId = 'ce06ca8f202eba80bc6d';
    const redirectUri = 'http://127.0.0.1:5000';
    const githubOAuthUrl = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}`;

    window.location.href = githubOAuthUrl;
  }

  handleLogin = async (e) => {
    e.preventDefault();
    try {
      const { username, password } = this.state;
      const serverUrl = process.env.REACT_APP_SERVER_URL;
      
      console.log('Fetching:', `${REACT_APP_SERVER_URL}/validate-credentials`);
      const response = await fetch(`${serverUrl}/validate-credentials`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });
  
      if (response.status === 200) {
        // Redirect to hello.html only if credentials are valid
        window.location.href = 'http://127.0.0.1:5000';
      } else {
        this.setState({ error: 'Invalid credentials' });
      }
    } catch (error) {
      // Handle errors as before
      console.error('Error:', error);
    }
  }
  

  render() {
    const backgroundStyle = {
      backgroundColor: '#f4f4f4',
      height: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
    };
    const textFieldStyle = {
      background: 'rgba(255, 255, 255, 0.7)',
      borderRadius: '5px',
    };

    return (
      <Box component="div" style={backgroundStyle}>
        <Container component="main" maxWidth="xs">
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" alt="GitHub Logo" width="100" height="100" />

            <Box
              component="form"
              onSubmit={this.handleLogin}
              sx={{ mt: 3 }}
            >
              <InputLabel htmlFor="username">Username</InputLabel>
              <TextField
                margin="normal"
                required
                fullWidth
                id="username"
                label="Username"
                name="username"
                value={this.state.username}
                onChange={this.handleChange}
                sx={textFieldStyle}
              />
              <InputLabel htmlFor="password">Password</InputLabel>
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                value={this.state.password}
                onChange={this.handleChange}
                sx={textFieldStyle}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                onClick={this.handleGitHubLogin}
              >
                Sign In with GitHub
              </Button>
              {this.state.error && (
                <p style={{ color: 'red' }}>{this.state.error}</p>
              )}
            </Box>
          </Box>
        </Container>
      </Box>
    );
  }
}

export default Login;
