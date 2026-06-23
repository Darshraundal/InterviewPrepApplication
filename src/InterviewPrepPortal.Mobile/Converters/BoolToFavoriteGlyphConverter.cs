using System.Globalization;

namespace InterviewPrepPortal.Mobile.Converters;

public class BoolToFavoriteGlyphConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture) =>
        value is true ? "★" : "☆";

    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture) =>
        throw new NotSupportedException();
}
