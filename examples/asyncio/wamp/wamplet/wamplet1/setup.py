from setuptools import setup, find_packages

setup(
    name='wamplet1',
    version='0.0.1',
    description='A demo WAMPlet.',
    platforms=['Any'],
    packages=find_packages(),
    entry_points={
        'autobahn.asyncio.wamplet': [
            'component1 = wamplet1.component1:make'
        ],
    },
    zip_safe=False,
)
