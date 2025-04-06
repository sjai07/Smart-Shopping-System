import React, { useState, useEffect } from 'react'
import { Typography, Grid, Card, CardContent, CardMedia, CardActions, Button, Box, CircularProgress, Alert } from '@mui/material'
import axios from 'axios'

function Recommendations() {
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchRecommendations()
  }, [])

  const fetchRecommendations = async () => {
    try {
      setLoading(true)
      setError(null)
      // Using a temporary customer ID for demo purposes
      const response = await axios.get('http://localhost:8000/recommendations/1')
      setRecommendations(response.data)
    } catch (err) {
      setError('Failed to fetch recommendations. Please try again later.')
      console.error('Error fetching recommendations:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Your Personalized Recommendations
      </Typography>

      <Grid container spacing={3}>
        {recommendations.map((item) => (
          <Grid item xs={12} sm={6} md={4} key={item.product_id}>
            <Card>
              <CardMedia
                component="img"
                height="140"
                image={`https://via.placeholder.com/300x140?text=${item.name}`}
                alt={item.name}
              />
              <CardContent>
                <Typography gutterBottom variant="h6" component="div">
                  {item.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Category: {item.category}
                </Typography>
                <Typography variant="h6" color="primary">
                  ${item.price.toFixed(2)}
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" color="primary">
                  View Details
                </Button>
                <Button size="small" color="secondary">
                  Add to Cart
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {recommendations.length === 0 && (
        <Typography variant="body1" sx={{ mt: 2, textAlign: 'center' }}>
          No recommendations available at the moment. Please check back later.
        </Typography>
      )}
    </Box>
  )
}

export default Recommendations