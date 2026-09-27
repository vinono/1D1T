// Render a captured, real TTY run of `1d1t welcome` into the shared site image.
// Usage: clang -fobjc-arc -framework AppKit scripts/render_welcome.m -o /tmp/render-welcome
//        /tmp/render-welcome <capture> <png>
#import <AppKit/AppKit.h>

static NSColor *colorForCode(NSString *code) {
    if ([code containsString:@"90"]) return [NSColor colorWithCalibratedRed:0.56 green:0.56 blue:0.56 alpha:1];
    if ([code containsString:@"97"]) return [NSColor colorWithCalibratedRed:0.97 green:0.97 blue:0.97 alpha:1];
    return [NSColor colorWithCalibratedRed:0.81 green:0.81 blue:0.81 alpha:1];
}

static NSAttributedString *styledLine(NSString *line, NSFont *regular, NSFont *bold) {
    NSMutableAttributedString *result = [[NSMutableAttributedString alloc] init];
    NSRegularExpression *ansi = [NSRegularExpression regularExpressionWithPattern:@"\\x1b\\[([0-9;]*)m" options:0 error:nil];
    NSArray<NSTextCheckingResult *> *matches = [ansi matchesInString:line options:0 range:NSMakeRange(0, line.length)];
    NSUInteger position = 0;
    NSString *code = @"37";
    for (NSTextCheckingResult *match in matches) {
        if (match.range.location > position) {
            NSString *part = [line substringWithRange:NSMakeRange(position, match.range.location - position)];
            [result appendAttributedString:[[NSAttributedString alloc] initWithString:part attributes:@{
                NSFontAttributeName: [code containsString:@"1;"] ? bold : regular,
                NSForegroundColorAttributeName: colorForCode(code)
            }]];
        }
        NSString *next = [line substringWithRange:[match rangeAtIndex:1]];
        code = next.length ? next : @"37";
        position = NSMaxRange(match.range);
    }
    if (position < line.length) {
        [result appendAttributedString:[[NSAttributedString alloc] initWithString:[line substringFromIndex:position] attributes:@{
            NSFontAttributeName: [code containsString:@"1;"] ? bold : regular,
            NSForegroundColorAttributeName: colorForCode(code)
        }]];
    }
    return result;
}

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc != 3) return 2;
        NSString *capture = [NSString stringWithContentsOfFile:@(argv[1]) encoding:NSUTF8StringEncoding error:nil];
        if (!capture) return 3;
        capture = [capture stringByReplacingOccurrencesOfString:@"\r" withString:@""];
        NSRange firstNewline = [capture rangeOfString:@"\n"];
        if (firstNewline.location != NSNotFound && [capture hasPrefix:@"^D"]) {
            capture = [capture substringFromIndex:NSMaxRange(firstNewline)];
        }

        const NSInteger width = 1060, height = 675;
        NSBitmapImageRep *bitmap = [[NSBitmapImageRep alloc] initWithBitmapDataPlanes:NULL pixelsWide:width pixelsHigh:height bitsPerSample:8 samplesPerPixel:4 hasAlpha:YES isPlanar:NO colorSpaceName:NSCalibratedRGBColorSpace bytesPerRow:0 bitsPerPixel:0];
        NSGraphicsContext *context = [NSGraphicsContext graphicsContextWithBitmapImageRep:bitmap];
        [NSGraphicsContext saveGraphicsState];
        [NSGraphicsContext setCurrentContext:context];
        [[NSColor colorWithCalibratedRed:0.025 green:0.025 blue:0.025 alpha:1] setFill];
        NSRectFill(NSMakeRect(0, 0, width, height));

        NSBezierPath *frame = [NSBezierPath bezierPathWithRoundedRect:NSMakeRect(18, 18, width - 36, height - 36) xRadius:18 yRadius:18];
        [[NSColor colorWithCalibratedRed:0.055 green:0.055 blue:0.055 alpha:1] setFill];
        [frame fill];
        [[NSColor colorWithCalibratedRed:0.18 green:0.18 blue:0.18 alpha:1] setStroke];
        frame.lineWidth = 1;
        [frame stroke];
        [[NSColor colorWithCalibratedRed:0.15 green:0.15 blue:0.15 alpha:1] setStroke];
        NSBezierPath *divider = [NSBezierPath bezierPath];
        [divider moveToPoint:NSMakePoint(19, height - 75)];
        [divider lineToPoint:NSMakePoint(width - 19, height - 75)];
        [divider stroke];

        for (NSInteger i = 0; i < 3; i++) {
            NSBezierPath *dot = [NSBezierPath bezierPathWithOvalInRect:NSMakeRect(42 + 24 * i, height - 51, 11, 11)];
            [[NSColor colorWithCalibratedRed:0.36 + i * 0.11 green:0.36 + i * 0.11 blue:0.36 + i * 0.11 alpha:1] setFill];
            [dot fill];
        }
        NSFont *font = [NSFont fontWithName:@"Menlo-Regular" size:22] ?: [NSFont monospacedSystemFontOfSize:22 weight:NSFontWeightRegular];
        NSFont *bold = [NSFont fontWithName:@"Menlo-Bold" size:22] ?: [NSFont monospacedSystemFontOfSize:22 weight:NSFontWeightBold];
        NSDictionary *titleAttributes = @{NSFontAttributeName: [NSFont fontWithName:@"Menlo-Regular" size:15], NSForegroundColorAttributeName: colorForCode(@"90")};
        NSString *title = @"1d1t welcome";
        [title drawAtPoint:NSMakePoint((width - [title sizeWithAttributes:titleAttributes].width) / 2, height - 54) withAttributes:titleAttributes];
        [styledLine(@"$ 1d1t welcome", font, bold) drawAtPoint:NSMakePoint(59, height - 122)];

        NSArray<NSString *> *lines = [capture componentsSeparatedByString:@"\n"];
        NSInteger lineIndex = 0;
        for (NSString *line in lines) {
            if (lineIndex > 20) break;
            if (line.length) {
                [styledLine(line, font, bold) drawAtPoint:NSMakePoint(59, height - 157 - lineIndex * 28)];
            }
            lineIndex++;
        }
        [context flushGraphics];
        [NSGraphicsContext restoreGraphicsState];
        NSData *png = [bitmap representationUsingType:NSBitmapImageFileTypePNG properties:@{}];
        return [png writeToFile:@(argv[2]) atomically:YES] ? 0 : 4;
    }
}
