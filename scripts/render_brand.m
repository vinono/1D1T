// Draw brand assets from the six tile rows in a real `1d1t welcome` TTY capture.
// Usage: clang -fobjc-arc -framework AppKit scripts/render_brand.m -o /tmp/render-brand
//        /tmp/render-brand <capture> <wide-logo.png> <square-icon.png>
#import <AppKit/AppKit.h>

static NSColor *silver(void) {
    return [NSColor colorWithCalibratedRed:0.97 green:0.97 blue:0.97 alpha:1];
}

static NSArray<NSString *> *tileRows(NSString *capture) {
    NSRegularExpression *ansi = [NSRegularExpression regularExpressionWithPattern:@"\\x1b\\[[0-9;]*m" options:0 error:nil];
    NSMutableArray<NSString *> *rows = [NSMutableArray array];
    for (NSString *line in [capture componentsSeparatedByCharactersInSet:[NSCharacterSet newlineCharacterSet]]) {
        NSString *plain = [ansi stringByReplacingMatchesInString:line options:0 range:NSMakeRange(0, line.length) withTemplate:@""];
        if ([plain containsString:@"■"]) [rows addObject:plain];
    }
    return rows;
}

static NSBitmapImageRep *bitmap(NSInteger width, NSInteger height) {
    return [[NSBitmapImageRep alloc] initWithBitmapDataPlanes:NULL pixelsWide:width pixelsHigh:height bitsPerSample:8 samplesPerPixel:4 hasAlpha:YES isPlanar:NO colorSpaceName:NSCalibratedRGBColorSpace bytesPerRow:0 bitsPerPixel:0];
}

static void background(NSInteger width, NSInteger height, CGFloat radius) {
    [[NSColor colorWithCalibratedRed:0.035 green:0.035 blue:0.035 alpha:1] setFill];
    NSRectFill(NSMakeRect(0, 0, width, height));
    NSBezierPath *shape = [NSBezierPath bezierPathWithRoundedRect:NSMakeRect(1, 1, width - 2, height - 2) xRadius:radius yRadius:radius];
    [[NSColor colorWithCalibratedRed:0.055 green:0.055 blue:0.055 alpha:1] setFill];
    [shape fill];
}

static void drawTiles(NSArray<NSString *> *rows, NSRect rect) {
    NSUInteger columns = 0;
    for (NSString *row in rows) columns = MAX(columns, row.length);
    CGFloat stepX = rect.size.width / columns;
    CGFloat stepY = rect.size.height / rows.count;
    [silver() setFill];
    for (NSUInteger y = 0; y < rows.count; y++) {
        NSString *row = rows[y];
        for (NSUInteger x = 0; x < row.length; x++) {
            if ([row characterAtIndex:x] != 0x25A0) continue;
            NSRect tile = NSMakeRect(rect.origin.x + x * stepX + 1.7,
                                     rect.origin.y + (rows.count - 1 - y) * stepY + 2.2,
                                     stepX - 3.4, stepY - 4.4);
            NSRectFill(tile);
        }
    }
}

static BOOL save(NSBitmapImageRep *rep, NSString *path) {
    NSData *png = [rep representationUsingType:NSBitmapImageFileTypePNG properties:@{}];
    return [png writeToFile:path atomically:YES];
}

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc != 4) return 2;
        NSString *capture = [NSString stringWithContentsOfFile:@(argv[1]) encoding:NSUTF8StringEncoding error:nil];
        if (!capture) return 3;
        NSArray<NSString *> *rows = tileRows(capture);
        if (rows.count != 6) return 4;

        NSBitmapImageRep *wide = bitmap(1024, 265);
        [NSGraphicsContext saveGraphicsState];
        [NSGraphicsContext setCurrentContext:[NSGraphicsContext graphicsContextWithBitmapImageRep:wide]];
        background(1024, 265, 28);
        drawTiles(rows, NSMakeRect(15, 17, 994, 231));
        [NSGraphicsContext currentContext].imageInterpolation = NSImageInterpolationHigh;
        [NSGraphicsContext restoreGraphicsState];
        if (!save(wide, @(argv[2]))) return 5;

        NSBitmapImageRep *icon = bitmap(1254, 1254);
        [NSGraphicsContext saveGraphicsState];
        [NSGraphicsContext setCurrentContext:[NSGraphicsContext graphicsContextWithBitmapImageRep:icon]];
        background(1254, 1254, 240);
        NSBezierPath *chevron = [NSBezierPath bezierPath];
        [chevron moveToPoint:NSMakePoint(365, 920)];
        [chevron lineToPoint:NSMakePoint(535, 750)];
        [chevron lineToPoint:NSMakePoint(365, 580)];
        chevron.lineWidth = 58;
        chevron.lineCapStyle = NSLineCapStyleSquare;
        chevron.lineJoinStyle = NSLineJoinStyleMiter;
        [silver() setStroke];
        [chevron stroke];
        [silver() setFill];
        NSRectFill(NSMakeRect(690, 686, 126, 126));
        drawTiles(rows, NSMakeRect(147, 188, 960, 300));
        [NSGraphicsContext restoreGraphicsState];
        if (!save(icon, @(argv[3]))) return 6;
        return 0;
    }
}
