import SwiftUI

// Basic Animation
struct BasicAnimationView: View {
    @State private var isAnimating = false

    var body: some View {
        VStack {
            Circle()
                .fill(Color.blue)
                .frame(width: 100, height: 100)
                .scaleEffect(isAnimating ? 1.5 : 1.0)
                .animation(.easeInOut(duration: 1.0).repeatForever(autoreverses: true), value: isAnimating)

            Button("Start Animation") {
                isAnimating.toggle()
            }
        }
        .onAppear {
            isAnimating = true
        }
    }
}

// Spring Animation
struct SpringAnimationView: View {
    @State private var offset: CGFloat = 0

    var body: some View {
        VStack {
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.blue)
                .frame(width: 100, height: 100)
                .offset(y: offset)

            Button("Animate") {
                withAnimation(.spring(response: 0.5, dampingFraction: 0.6)) {
                    offset = offset == 0 ? 200 : 0
                }
            }
        }
    }
}

// Rotation Animation
struct RotationAnimationView: View {
    @State private var rotation: Double = 0

    var body: some View {
        VStack {
            Image(systemName: "arrow.right.circle.fill")
                .font(.system(size: 100))
                .rotationEffect(.degrees(rotation))
                .animation(.linear(duration: 2).repeatForever(autoreverses: false), value: rotation)

            Button("Rotate") {
                rotation += 360
            }
        }
        .onAppear {
            rotation = 360
        }
    }
}

// Fade Animation
struct FadeAnimationView: View {
    @State private var opacity: Double = 1.0

    var body: some View {
        VStack {
            Text("Fading Text")
                .font(.title)
                .opacity(opacity)

            Button("Toggle Fade") {
                withAnimation(.easeInOut(duration: 1.0)) {
                    opacity = opacity == 1.0 ? 0.0 : 1.0
                }
            }
        }
    }
}

// Slide Animation
struct SlideAnimationView: View {
    @State private var showDetails = false

    var body: some View {
        VStack {
            Button("Toggle Details") {
                withAnimation(.spring()) {
                    showDetails.toggle()
                }
            }

            if showDetails {
                VStack(alignment: .leading) {
                    Text("Detail 1")
                    Text("Detail 2")
                    Text("Detail 3")
                }
                .padding()
                .background(Color.gray.opacity(0.2))
                .cornerRadius(10)
                .transition(.slide)
            }
        }
        .padding()
    }
}

// Combined Animations
struct CombinedAnimationView: View {
    @State private var isAnimating = false

    var body: some View {
        VStack {
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.blue)
                .frame(width: isAnimating ? 200 : 100, height: isAnimating ? 200 : 100)
                .rotationEffect(.degrees(isAnimating ? 180 : 0))
                .offset(y: isAnimating ? -100 : 0)

            Button("Animate") {
                withAnimation(.spring(response: 0.6, dampingFraction: 0.7)) {
                    isAnimating.toggle()
                }
            }
        }
    }
}

// Matched Geometry Effect
struct MatchedGeometryEffectExample: View {
    @State private var isExpanded = false
    @Namespace private var animation

    var body: some View {
        VStack {
            if !isExpanded {
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color.blue)
                    .matchedGeometryEffect(id: "rectangle", in: animation)
                    .frame(width: 100, height: 100)
            } else {
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color.blue)
                    .matchedGeometryEffect(id: "rectangle", in: animation)
                    .frame(width: 300, height: 300)
            }

            Button("Toggle") {
                withAnimation(.spring()) {
                    isExpanded.toggle()
                }
            }
        }
    }
}

// Gesture Animation
struct GestureAnimationView: View {
    @State private var offset: CGSize = .zero

    var body: some View {
        Circle()
            .fill(Color.blue)
            .frame(width: 100, height: 100)
            .offset(offset)
            .gesture(
                DragGesture()
                    .onChanged { value in
                        offset = value.translation
                    }
                    .onEnded { _ in
                        withAnimation(.spring()) {
                            offset = .zero
                        }
                    }
            )
    }
}
