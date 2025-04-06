import React from 'react'
import { Typography, Grid, Paper, Box, Button } from '@mui/material'
import { useNavigate } from 'react-router-dom'

function Home() {
  const navigate = useNavigate()

  return (
    <Box>
      <Paper sx={{ p: 4, mb: 4, textAlign: 'center', backgroundColor: 'primary.main', color: 'white' }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Welcome to Smart Shopping
        </Typography>
        <Typography variant="h6" gutterBottom>
          Get personalized product recommendations based on your preferences
        </Typography>
        <Button
          variant="contained"
          color="secondary"
          size="large"
          onClick={() => navigate('/recommendations')}
          sx={{ mt: 2 }}
        >
          Get Started
        </Button>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              How It Works
            </Typography>
            <Typography paragraph>
              Our smart recommendation system analyzes your preferences and shopping behavior to suggest products you'll love. We integrate with major e-commerce platforms to provide you with the best shopping experience.
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Features
            </Typography>
            <Typography component="ul">
              <li>Personalized product recommendations</li>
              <li>Real-time price tracking</li>
              <li>Smart shopping lists</li>
              <li>Integration with major e-commerce platforms</li>
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Home