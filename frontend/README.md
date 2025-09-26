# AtoZ Bot Frontend

A modern, responsive React dashboard for the AtoZ Translation Bot built with TypeScript, Tailwind CSS, and Framer Motion.

## 🚀 Features

- **Modern Design System**: Built with Tailwind CSS and custom design tokens
- **Responsive Layout**: Mobile-first design that works on all devices
- **Dark/Light Mode**: Seamless theme switching with system preference detection
- **Real-time Updates**: Live bot status and metrics updates
- **Smooth Animations**: Framer Motion for delightful user interactions
- **Type Safety**: Full TypeScript support for better development experience
- **Performance Optimized**: Vite for fast development and optimized builds

## 🛠️ Tech Stack

- **React 18** - Modern React with hooks and concurrent features
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **React Router** - Client-side routing
- **React Query** - Data fetching and caching
- **Zustand** - State management
- **Lucide React** - Beautiful icons
- **Vite** - Fast build tool and dev server

## 📦 Installation

### Prerequisites

- Node.js 16 or higher
- npm, yarn, or pnpm

### Quick Start

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Run the setup script:**
   ```bash
   chmod +x install-deps.sh
   ./install-deps.sh
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

### Manual Installation

If you prefer to install dependencies manually:

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🎨 Design System

The frontend uses a comprehensive design system with:

### Colors
- **Primary**: Blue-based color palette for main actions
- **Secondary**: Gray-based palette for secondary elements
- **Success**: Green for positive states
- **Warning**: Yellow/Orange for caution states
- **Error**: Red for error states
- **Muted**: Subtle colors for less important content

### Typography
- **Font Family**: System fonts with fallbacks
- **Font Weights**: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)
- **Font Sizes**: Responsive scale from 12px to 48px

### Spacing
- **Base Unit**: 4px (0.25rem)
- **Scale**: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96px

### Components
- **Cards**: Elevated surfaces with subtle shadows
- **Buttons**: Multiple variants with hover states
- **Forms**: Consistent input styling
- **Navigation**: Responsive sidebar with mobile support

## 📱 Responsive Design

The dashboard is fully responsive with breakpoints:

- **xs**: 475px (small phones)
- **sm**: 640px (large phones)
- **md**: 768px (tablets)
- **lg**: 1024px (laptops)
- **xl**: 1280px (desktops)
- **2xl**: 1536px (large desktops)
- **3xl**: 1600px (ultra-wide)

## 🌙 Dark Mode

The application supports both light and dark modes:

- **System Preference**: Automatically detects user's system preference
- **Manual Toggle**: Users can manually switch themes
- **Persistent**: Theme preference is saved in localStorage
- **Smooth Transitions**: All color changes are animated

## 🎭 Animations

Smooth animations powered by Framer Motion:

- **Page Transitions**: Fade and slide effects
- **Component Animations**: Staggered loading animations
- **Hover Effects**: Subtle scale and shadow changes
- **Loading States**: Spinner and skeleton animations

## 🔧 Development

### Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── dashboard/       # Dashboard-specific components
│   │   ├── layout/          # Layout components
│   │   └── ui/             # Base UI components
│   ├── pages/              # Page components
│   ├── services/           # API services
│   ├── stores/             # State management
│   ├── styles/             # Global styles
│   ├── types/              # TypeScript type definitions
│   └── utils/              # Utility functions
├── public/                 # Static assets
├── tailwind.config.js      # Tailwind configuration
├── postcss.config.js       # PostCSS configuration
├── vite.config.ts          # Vite configuration
└── package.json            # Dependencies and scripts
```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

### Code Style

The project follows these conventions:

- **TypeScript**: Strict mode enabled
- **ESLint**: Configured with React and TypeScript rules
- **Prettier**: Code formatting (if configured)
- **Import Order**: External → Internal → Relative
- **Component Structure**: Props → State → Effects → Handlers → Render

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

This creates an optimized production build in the `dist` directory.

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### Docker Deployment

The project includes a Dockerfile for containerized deployment:

```bash
# Build Docker image
docker build -t atoz-bot-frontend .

# Run container
docker run -p 3000:3000 atoz-bot-frontend
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:

1. Check the console for errors
2. Verify all dependencies are installed
3. Ensure Node.js version is 16 or higher
4. Check the browser compatibility

For additional help, please open an issue in the repository.
