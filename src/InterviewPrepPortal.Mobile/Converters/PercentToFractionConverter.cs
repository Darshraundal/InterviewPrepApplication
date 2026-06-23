using System.Globalization;

namespace InterviewPrepPortal.Mobile.Converters;

/// <summary>Converts a 0-100 percentage value into the 0.0-1.0 fraction ProgressBar expects.</summary>
public class PercentToFractionConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        var percent = System.Convert.ToDouble(value ?? 0d);
        return percent / 100.0;
    }

    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture) =>
        throw new NotSupportedException();
}
