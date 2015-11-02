<Query Kind="Program">
  <Reference>&lt;RuntimeDirectory&gt;\System.Runtime.dll</Reference>
  <NuGetReference>Rx-Main</NuGetReference>
  <Namespace>System.Reactive.Linq</Namespace>
</Query>

void Main()
{
	// Pick an initial period, it can be changed later.
	var intervalPeriod = TimeSpan.FromSeconds(1);

	// Create an observable using a functor that captures the interval period.
	var o = ObservableFromIntervalFunctor(() => intervalPeriod);

	// Log every value so we can visualize the observable.
	o.Subscribe(Console.WriteLine);

	// Sleep for a while so you can observe the observable.
	Thread.Sleep(TimeSpan.FromSeconds(5.0));

	// Changing the interval period will takes effect on next tick.
	intervalPeriod = TimeSpan.FromSeconds(0.3);

}

IObservable<long> ObservableFromIntervalFunctor(Func<TimeSpan> intervalPeriodFunctor)
{
	return Observable.Generate(0L, s => true, s => s + 1, s => s, s => intervalPeriodFunctor());
}