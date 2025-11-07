import 'package:flutter/material.dart';

class HeroAnimationExample extends StatelessWidget {
  const HeroAnimationExample({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: 10,
      itemBuilder: (context, index) {
        return ListTile(
          leading: Hero(
            tag: 'image-$index',
            child: CircleAvatar(
              backgroundImage: NetworkImage(
                'https://picsum.photos/100?random=$index',
              ),
            ),
          ),
          title: Text('Item $index'),
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => DetailPage(index: index),
              ),
            );
          },
        );
      },
    );
  }
}

class DetailPage extends StatelessWidget {
  final int index;

  const DetailPage({Key? key, required this.index}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Detail $index')),
      body: Center(
        child: Hero(
          tag: 'image-$index',
          child: Image.network(
            'https://picsum.photos/300?random=$index',
            width: 300,
            height: 300,
          ),
        ),
      ),
    );
  }
}

class CustomHeroFlightShuttleBuilder extends StatelessWidget {
  const CustomHeroFlightShuttleBuilder({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Hero(
      tag: 'custom-hero',
      flightShuttleBuilder: (
        flightContext,
        animation,
        flightDirection,
        fromHeroContext,
        toHeroContext,
      ) {
        return ScaleTransition(
          scale: animation.drive(
            Tween<double>(begin: 0.5, end: 1.0).chain(
              CurveTween(curve: Curves.easeInOut),
            ),
          ),
          child: toHeroContext.widget,
        );
      },
      child: Container(
        width: 100,
        height: 100,
        color: Colors.blue,
      ),
    );
  }
}

class PhotoHeroExample extends StatelessWidget {
  final String imageUrl;
  final VoidCallback onTap;
  final double width;

  const PhotoHeroExample({
    Key? key,
    required this.imageUrl,
    required this.onTap,
    this.width = 100,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      child: Hero(
        tag: imageUrl,
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: onTap,
            child: Image.network(
              imageUrl,
              fit: BoxFit.cover,
            ),
          ),
        ),
      ),
    );
  }
}
